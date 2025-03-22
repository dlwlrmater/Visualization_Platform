# Visualization_Platform / 可视化平台

## 项目介绍

这是一个基于Python和Html的对于Shapefile格式数据的可视化平台。只要提供的是带有坐标，并且数据位置和空间位置保持一致的情况下的Shapefile文件，都可以反映在以高德地图为底图的窗口上。

项目开始是为了脱离GIS相关平台，方便数据展示和对特定要素进行查询。

## 项目特点

- 脱离GIS，矢量数据网页展示
- 可切换多种国内源底图，包含标准地图和卫星影像图
- 自带坐标转换，方便适配底图
- 界面要素及状态可保存，省去二次加载时间
- 根据分层目录筛选特定图层展示
- 鼠标放到要素上可以显示图层信息

## 项目预览

<img src="C:\Users\win\Desktop\VP\3.功能介绍.png" style="zoom:30%;" />

- **左上角绿色：更换地图**

  - 图层筛选
  - 缩放至已展示图层
  - 保存/导出当前状态JSON文件

- **右上角黑色：要素筛选**

  - 根据static/data/extra下各个级别文件夹名称进行筛选

    e.g  如果有文件存在 **static/data/extra/A/B/C/Z.shp**，时间行下拉菜单会出现**A**，类型行下拉菜单会出现**B**，状态行下拉菜单会出现**C**，如果只有文件夹但是**没有文件**出现在第三级别文件夹内，文件路径不会被读取到筛选控件内

  - 下拉筛选控件可以多选

- **左下角蓝色：要素展示（Extra）**

  - extra文件夹内经过筛选之后的文件展示
  - 可以通过勾选打开/关闭图层，每当图层打开与关闭，右下角图例同步更新

- **左下角黄色：要素展示（Plan）**

  - plan文件夹内所有图层展示
  - 可以通过勾选打开/关闭图层，每当图层打开与关闭，右下角图例同步更新

- **左下角红色：要素展示（Current）**

  - current文件夹内所有图层展示
  - 可以通过勾选打开/关闭图层，每当图层打开与关闭，右下角图例同步更新

- **右下角黑色：图例**

  - 图层名称为：图层名+一级目录+二级目录+三级目录
  - 颜色为随机值

  

## 项目结构

```
├── app.py            			        	  # 主文件
├── requestments.txt 			       	   	  # 依赖项文件
├── README.md       			         	    # 项目说明文件
├── templates/         			        	  # HTML 模板目录
│   └── index.html      			          # 主页面模板
├── trans_coordts.py     			     	    # 坐标转换程序  任何带有坐标的矢量 ——→ GCJ02坐标系
├── Input        	  						        # 需要进行坐标转换的数据
│   └── data/           			       	  # 坐标转换-数据目录
│       ├── base/        			      	  # 坐标转换-基础数据
│       │   ├── current/    			   	  # 坐标转换-当前数据
│       │   └── plan/          				  # 坐标转换-规划数据
│       └── extra/             				  # 坐标转换-额外数据
│           └── A/                		  # 坐标转换-额外数据-一级目录
│              └── B/     	 			 	    # 坐标转换-额外数据-二级目录
│                  └── C/   			      # 坐标转换-额外数据-三级目录
│                   	└── xxx.cpg 	    # 坐标转换-额外数据-数据要素
│                   	└── xxx.dbf 	    # 坐标转换-额外数据-数据要素
│                   	└── xxx.prj 	    # 坐标转换-额外数据-数据要素
│                   	└── xxx.shp 	    # 坐标转换-额外数据-数据要素
│                   	└── xxx.shx 	    # 坐标转换-额外数据-数据要素	      
└── static/                 			      # 静态资源目录
    └── *data/              			   	  # 数据目录
        ├── *base/           	 			    # 基础数据
        │   ├── *current/   			  	  # 当前数据
        │   └── *plan/        			 	  # 规划数据
        └── *extra/         			   	  # 额外数据
            └── A/            				  # 额外数据-一级目录
               └── B/     	  				  # 额外数据-二级目录
                   └── C/     				  # 额外数据-三级目录
                	   	└── xxx.cpg 	    # 额外数据-数据要素
            	       	└── xxx.dbf 	    # 额外数据-数据要素
                      └── xxx.prj   	  # 额外数据-数据要素
    	               	└── xxx.shp 		  # 额外数据-数据要素
	           	      	└── xxx.shx 		  # 额外数据-数据要素            

· extra下面文件夹可以随意修改，但目前支持固定三级目录下文件读取及展示
· 文件夹内为示例文件（上海地铁）
· static下星号文件夹为必须存在文件夹，如主程序未改动，这些文件夹名也不必改动
```

## 项目启动

```
· 如果提供数据不是GCJ-02坐标，把数据根据实际存在位置放到 Input 文件夹中
python trans_coordts.py
结果会按照Input里面的格式放到static/data下面的对应文件中

· 运行程序
python app.py
```

## 贡献指南

目前还有很多不完善的地方，如果在使用过程中存在任何BUG，欢迎提交Issue和Pull request帮助改进项目。

## 更新日志

### 2025.03.20

更新坐标转换部分代码及readme
