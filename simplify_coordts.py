import geopandas as gpd
import os
from pathlib import Path
import shutil
import math
from shapely.geometry import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon, GeometryCollection
import shapely.wkb
import shapely.geometry
import shapely.ops

def wgs84_to_gcj02(lng, lat):
    """
    WGS84坐标系转GCJ02坐标系
    :param lng: WGS84坐标系下的经度
    :param lat: WGS84坐标系下的纬度
    :return: 转换后的GCJ02下经纬度
    """
    PI = 3.1415926535897932384626
    a = 6378245.0  # 长半轴
    ee = 0.00669342162296594323  # 偏心率平方
    
    if out_of_china(lng, lat):  # 判断是否在国内
        return lng, lat
    
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * PI)
    mglat = lat + dlat
    mglng = lng + dlng
    return mglng, mglat

def out_of_china(lng, lat):
    """判断是否在国内"""
    return not (73.66 < lng < 135.05 and 3.86 < lat < 53.55)

def transform_lat(lng, lat):
    PI = 3.1415926535897932384626
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * PI) + 40.0 *
            math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * PI) + 320 *
            math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret

def transform_lng(lng, lat):
    PI = 3.1415926535897932384626
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * PI) + 40.0 *
            math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * PI) + 300.0 *
            math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret

def convert_geometry_to_gcj02(geometry):
    """将Shapely几何对象从WGS84转换为GCJ02，支持复合几何类型和三维数据"""
    if geometry is None or geometry.is_empty:
        return geometry
    
    # 首先处理三维几何，将其转换为二维
    if hasattr(geometry, 'has_z') and geometry.has_z:
        # print(f"检测到三维几何: {type(geometry).__name__}，转换为二维")
        geometry = shapely.geometry.shape(shapely.wkb.loads(shapely.wkb.dumps(geometry, output_dimension=2)))
    
    # 处理简单几何类型
    if isinstance(geometry, Point):
        lng, lat = wgs84_to_gcj02(geometry.x, geometry.y)
        return Point(lng, lat)
    
    elif isinstance(geometry, LineString):
        new_coords = []
        for x, y in geometry.coords:
            lng, lat = wgs84_to_gcj02(x, y)
            new_coords.append((lng, lat))
        return LineString(new_coords)
    
    elif isinstance(geometry, Polygon):
        try:
            exterior_coords = []
            for x, y in geometry.exterior.coords:
                lng, lat = wgs84_to_gcj02(x, y)
                exterior_coords.append((lng, lat))
            
            interiors = []
            for interior in geometry.interiors:
                interior_coords = []
                for x, y in interior.coords:
                    lng, lat = wgs84_to_gcj02(x, y)
                    interior_coords.append((lng, lat))
                interiors.append(interior_coords)
            
            return Polygon(exterior_coords, interiors)
        except Exception as e:
            print(f"处理Polygon出错: {e}")
            return geometry
    
    # 处理复合几何类型
    elif isinstance(geometry, MultiPoint):
        points = []
        for point in geometry.geoms:
            points.append(convert_geometry_to_gcj02(point))
        return MultiPoint(points)
    
    elif isinstance(geometry, MultiLineString):
        lines = []
        for line in geometry.geoms:
            lines.append(convert_geometry_to_gcj02(line))
        return MultiLineString(lines)
    
    elif isinstance(geometry, MultiPolygon):
        polygons = []
        for polygon in geometry.geoms:
            polygons.append(convert_geometry_to_gcj02(polygon))
        return MultiPolygon(polygons)
    
    elif isinstance(geometry, GeometryCollection):
        geometries = []
        for geom in geometry.geoms:
            geometries.append(convert_geometry_to_gcj02(geom))
        return GeometryCollection(geometries)
    
    else:
        print(f"警告: 未知几何类型 {type(geometry)}，无法转换坐标")
        return geometry

def process_shapefile(input_path, output_path):
    """处理单个shapefile文件并转换坐标"""
    try:
        # 读取shapefile
        gdf = gpd.read_file(input_path)
        
        # 确保有geometry列
        if 'geometry' not in gdf.columns:
            print(f"警告: {input_path} 没有geometry列")
            return
        
        # 确保坐标系是WGS84
        if gdf.crs:
            if gdf.crs != "EPSG:4326":
                print(f"转换坐标系: {gdf.crs} -> WGS84")
                gdf = gdf.to_crs("EPSG:4326")
        else:
            print(f"警告: {input_path} 没有坐标系信息，假设为WGS84")
            gdf.crs = "EPSG:4326"
        
        # 融合所有几何要素
        print(f"融合要素: {len(gdf)} 个要素")
        print(input_path)
        try:
            # 检查几何类型
            geom_type = gdf.geometry.iloc[0].geom_type
            print(f"几何类型: {geom_type}")
            
            # 根据几何类型选择不同的处理方法
            if geom_type in ['Point', 'MultiPoint']:
                # 点类型：收集所有点并转换坐标
                all_points = []
                for geom in gdf.geometry:
                    converted_geom = convert_geometry_to_gcj02(geom)
                    if isinstance(converted_geom, Point):
                        all_points.append(converted_geom)
                    elif isinstance(converted_geom, MultiPoint):
                        all_points.extend(list(converted_geom.geoms))
                merged_geom = MultiPoint(all_points)
                
            elif geom_type in ['LineString', 'MultiLineString']:
                # 线类型：收集所有线并转换坐标
                all_lines = []
                for geom in gdf.geometry:
                    converted_geom = convert_geometry_to_gcj02(geom)
                    if isinstance(converted_geom, LineString):
                        all_lines.append(converted_geom)
                    elif isinstance(converted_geom, MultiLineString):
                        all_lines.extend(list(converted_geom.geoms))
                merged_geom = MultiLineString(all_lines)
                
            elif geom_type in ['Polygon', 'MultiPolygon']:
                # 面类型：先转换坐标，再融合
                converted_geoms = []
                for geom in gdf.geometry:
                    # 先转换坐标
                    converted_geom = convert_geometry_to_gcj02(geom)
                    if isinstance(converted_geom, (Polygon, MultiPolygon)):
                        if isinstance(converted_geom, Polygon):
                            converted_geoms.append(converted_geom)
                        else:
                            converted_geoms.extend(list(converted_geom.geoms))
                
                # 使用unary_union融合所有转换后的面
                merged_geom = shapely.ops.unary_union(converted_geoms)
                
                # 确保结果是Polygon或MultiPolygon
                if not isinstance(merged_geom, (Polygon, MultiPolygon)):
                    print(f"警告: 融合后的几何类型不是Polygon或MultiPolygon: {type(merged_geom)}")
                    return
                
                # 如果是单个Polygon，转换为MultiPolygon
                if isinstance(merged_geom, Polygon):
                    merged_geom = MultiPolygon([merged_geom])
            else:
                print(f"警告: 不支持的几何类型 {geom_type}")
                return
            
            # 创建新的GeoDataFrame
            dissolved_gdf = gpd.GeoDataFrame({'id': [0], 'geometry': [merged_geom]}, crs=gdf.crs)
            
        except Exception as e:
            print(f"融合几何要素时出错: {e}")
            return
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 保存处理后的文件
        dissolved_gdf.to_file(output_path)
        print(f"成功处理: {input_path}")
        
    except Exception as e:
        print(f"处理 {input_path} 时出错: {e}")

def process_all_shapefiles(input_root, output_root):
    """处理所有shapefile文件"""
    # 转换为Path对象
    input_root = Path(input_root)
    output_root = Path(output_root)
    
    # 确保输出根目录存在
    output_root.mkdir(parents=True, exist_ok=True)
    
    # 遍历所有.shp文件
    for shp_file in input_root.rglob('*.shp'):
        # 计算相对路径
        rel_path = shp_file.relative_to(input_root)
        # 构建输出路径
        output_path = output_root / rel_path
        
        # 处理文件
        process_shapefile(str(shp_file), str(output_path))

def main():
    # 定义输入和输出根目录
    input_root = r"D:\!platform\Visualization Platform\!input"
    output_root = r"D:\!platform\Visualization Platform\static"
    
    try:
        # 处理所有shapefile文件
        process_all_shapefiles(input_root, output_root)
        print("处理完成！")
        
    except Exception as e:
        print(f"发生错误: {e}")

def list_all_subfolders_in_year(directory):
    """
    获取指定目录下的三级子文件夹
    返回: (first_level_folders, second_level_folders, third_level_folders)
    """
    first_level = set()
    second_level = set()
    third_level = set()
    
    try:
        # 确保目录存在
        if not os.path.exists(directory):
            print(f"目录不存在: {directory}")
            return [], [], []
        
        # 遍历目录
        for root, dirs, files in os.walk(directory):
            # 计算当前目录相对于基础目录的深度
            rel_path = os.path.relpath(root, directory)
            if rel_path == '.':
                continue
                
            parts = rel_path.split(os.sep)
            
            # 根据深度将文件夹名添加到对应集合
            if len(parts) >= 1:
                first_level.add(parts[0])
            if len(parts) >= 2:
                second_level.add(parts[1])
            if len(parts) >= 3:
                third_level.add(parts[2])
    
    except Exception as e:
        print(f"遍历目录失败 {directory}: {str(e)}")
        return [], [], []
    
    # 转换为排序后的列表
    return (
        sorted(list(first_level)),
        sorted(list(second_level)),
        sorted(list(third_level))
    )

if __name__ == "__main__":
    main()
