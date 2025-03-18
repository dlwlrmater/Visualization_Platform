from flask import Flask, render_template, jsonify, request
import geopandas as gpd
import ezdxf
import os
from shapely.geometry import LineString, Point, Polygon
import glob
from pathlib import Path
from functools import lru_cache

app = Flask(__name__)

# 定义 data 文件夹路径
DATA_DIR = os.path.join("static", "data")

def get_shapefile_paths(directory):
    """获取目录下所有shapefile的路径"""
    return [str(p) for p in Path(directory).rglob("*.shp")]

@lru_cache(maxsize=None)
def load_shapefiles(directory):
    """加载所有 .shp 文件"""
    print(f"开始加载目录: {directory}")
    shapefiles = get_shapefile_paths(directory)
    print(f"找到 {len(shapefiles)} 个shapefile文件")
    
    layers = {}
    for shp_path in shapefiles:
        try:
            # 用相对路径作为图层名称
            layer_name = os.path.relpath(shp_path, DATA_DIR).replace(os.sep, "__")
            
            # 读取 shapefile
            print(f"正在加载: {shp_path}")
            gdf = gpd.read_file(shp_path)
            
            layer_name1 = layer_name.split('.')[0]
            layer_name1 = layer_name1.rsplit('__',1)
            layer_name1 = layer_name1[1] + '__' + layer_name1[0]
            layers[layer_name1] = gdf
            print(f"成功加载图层: {layer_name1}")
        except Exception as e:
            print(f"加载shapefile失败 {shp_path}: {str(e)}")
    return layers

def get_subfolders(directory):
    """获取指定文件夹中的所有子文件夹名称"""
    subfolders = [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]
    return subfolders

def list_all_subfolders_in_year(root_path):
    """获取指定目录下的三级子文件夹"""
    target_path = Path(root_path) / "static" / "data" / "extra"
    if not target_path.exists():
        print(f"路径 {target_path} 不存在")
        return [], [], []

    # 初始化三个集合，使用集合避免重复
    first_level = set()
    second_level = set()
    third_level = set()

    try:
        # 只遍历一次目录结构
        for path in target_path.iterdir():
            if path.is_dir():
                # 第一级目录
                first_level.add(path.name)
                
                # 第二级目录
                for second_path in path.iterdir():
                    if second_path.is_dir():
                        second_level.add(second_path.name)
                        
                        # 第三级目录
                        for third_path in second_path.iterdir():
                            if third_path.is_dir():
                                third_level.add(third_path.name)
    except Exception as e:
        print(f"遍历目录失败: {e}")

    # 转换为排序后的列表
    return (
        sorted(list(first_level)),
        sorted(list(second_level)),
        sorted(list(third_level))
    )

@app.route('/')
def index():
    """渲染主页面"""
    return render_template('index.html')

@app.route('/base/current-layers')
def base_current_layers():
    """返回 current 文件夹下的所有 SHP 文件数据"""
    current_dir = os.path.join(DATA_DIR, "base", "current")
    shapefile_layers = load_shapefiles(current_dir)
    return jsonify({
        "current_shapefiles": {
            layer_name: layer.to_json()
            for layer_name, layer in shapefile_layers.items()
        }
    })

@app.route('/base/plan-layers')
def base_plan_layers():
    """返回 plan 文件夹下的所有 SHP 文件数据"""
    plan_dir = os.path.join(DATA_DIR, "base", "plan")
    shapefile_layers = load_shapefiles(plan_dir)
    return jsonify({
        "plan_shapefiles": {
            layer_name: layer.to_json()
            for layer_name, layer in shapefile_layers.items()
        }
    })

@app.route('/filter', methods=['POST'])
def filter_data():
    selected_first_level = request.form.getlist('first_level[]')
    selected_second_level = request.form.getlist('second_level[]')
    selected_third_level = request.form.getlist('third_level[]')

    # 优化：先检查选择是否有效
    if not all([selected_first_level, selected_second_level, selected_third_level]):
        return jsonify({"error": "请在所有三个下拉框中都选择至少一个选项"})

    # 优化：使用集合来存储已处理的路径，避免重复加载
    filtered_layers = {}
    processed_paths = set()
    
    extra_dir = os.path.join(DATA_DIR, "extra")
    for first_level in selected_first_level:
        for second_level in selected_second_level:
            for third_level in selected_third_level:
                folder_path = os.path.join(extra_dir, first_level, second_level, third_level)
                
                # 检查路径是否已经处理过
                if folder_path in processed_paths:
                    continue
                    
                if os.path.exists(folder_path):
                    print(f"检查文件夹: {folder_path}")
                    shapefile_layers = load_shapefiles(folder_path)
                    filtered_layers.update(shapefile_layers)
                    processed_paths.add(folder_path)
    
    # 转换为JSON格式
    return jsonify({
        layer_name: layer.to_json()
        for layer_name, layer in filtered_layers.items()
    })

@app.route('/extra-folders')
def get_extra_folders():
    """返回 extra 文件夹中的所有子文件夹名称"""
    extra_dir = os.path.join(DATA_DIR, "extra")
    subfolders = get_subfolders(extra_dir)
    return jsonify(subfolders)

@app.route('/extra-folder-levels')
def get_extra_folder_levels():
    """返回 extra 文件夹中的所有层级文件夹名称"""
    first_level, second_level, third_level = list_all_subfolders_in_year(".")
    return jsonify({
        "first_level": first_level,
        "second_level": second_level,
        "third_level": third_level
    })

if __name__ == '__main__':
    import threading
    import webbrowser
    import time
    
    def open_browser():
        """在服务器启动后打开浏览器"""
        time.sleep(1)
        webbrowser.open_new('http://127.0.0.1:5000/')
    
    threading.Thread(target=open_browser).start()
    app.run(debug=False)
