# Visualization_Platform / 可视化平台

**Read this in other languages: [English](README_eng.md), [中文](README.md).**


## Project Introduction

This is a visualization platform for Shapefile format data based on Python and HTML. As long as the provided Shapefile files have coordinates and the data location is consistent with the spatial location, they can be displayed on a window with Amap as the base map.

The project started to facilitate data display and query specific features without relying on GIS-related platforms.

## Project Features

- Vector data web display independent of GIS
- Multiple domestic base maps to choose from, including standard maps and satellite imagery
- Built-in coordinate conversion for easy adaptation to base maps
- Interface elements and states can be saved, eliminating secondary loading time
- Filter specific layers for display based on hierarchical directories
- Hover mouse over features to display layer information

## Project Preview

<img src="C:\Users\win\Desktop\VP\3.功能介绍.png" style="zoom:30%;" />

- **Top-left green: Change Map**
  - Layer filtering
  - Zoom to displayed layers
  - Save/export current state JSON file

- **Top-right black: Feature Filtering**
  - Filter based on folder names at each level under static/data/extra
    
    e.g., If a file exists at **static/data/extra/A/B/C/Z.shp**, the Time dropdown menu will show **A**, the Type dropdown menu will show **B**, and the Status dropdown menu will show **C**. If there are only folders but **no files** in the third-level folder, the file path will not be loaded into the filtering control.
    
  - Multiple selections are allowed in dropdown filtering controls

- **Bottom-left blue: Feature Display (Extra)**
  - Display of filtered files from the extra folder
  - Layers can be turned on/off by checking, and the legend in the bottom-right updates accordingly

- **Bottom-left yellow: Feature Display (Plan)**
  - Display of all layers in the plan folder
  - Layers can be turned on/off by checking, and the legend in the bottom-right updates accordingly

- **Bottom-left red: Feature Display (Current)**
  - Display of all layers in the current folder
  - Layers can be turned on/off by checking, and the legend in the bottom-right updates accordingly

- **Bottom-right black: Legend**
  - Layer name format: layer name + first-level directory + second-level directory + third-level directory
  - Colors are randomly assigned

## Project Structure

```
├── app.py                              # Main file
├── requestments.txt                    # Dependencies file
├── README.md                           # Project documentation
├── templates/                          # HTML template directory
│   └── index.html                      # Main page template
├── trans_coordts.py                    # Coordinate conversion program (Any vector with coordinates → GCJ02 coordinate system)
├── Input                               # Data needing coordinate conversion
│   └── data/                           # Coordinate conversion - data directory
│       ├── base/                       # Coordinate conversion - base data
│       │   ├── current/                # Coordinate conversion - current data
│       │   └── plan/                   # Coordinate conversion - planning data
│       └── extra/                      # Coordinate conversion - extra data
│           └── A/                      # Coordinate conversion - extra data - first level directory
│              └── B/                   # Coordinate conversion - extra data - second level directory
│                  └── C/               # Coordinate conversion - extra data - third level directory
│                     └── xxx.cpg       # Coordinate conversion - extra data - data element
│                     └── xxx.dbf       # Coordinate conversion - extra data - data element
│                     └── xxx.prj       # Coordinate conversion - extra data - data element
│                     └── xxx.shp       # Coordinate conversion - extra data - data element
│                     └── xxx.shx       # Coordinate conversion - extra data - data element	      
└── static/                             # Static resources directory
    └── *data/                          # Data directory
        ├── *base/                      # Base data
        │   ├── *current/               # Current data
        │   └── *plan/                  # Planning data
        └── *extra/                     # Extra data
            └── A/                      # Extra data - first level directory
               └── B/                   # Extra data - second level directory
                   └── C/               # Extra data - third level directory
                      └── xxx.cpg       # Extra data - data element
                      └── xxx.dbf       # Extra data - data element
                      └── xxx.prj       # Extra data - data element
                      └── xxx.shp       # Extra data - data element
                      └── xxx.shx       # Extra data - data element
                      
· Folders under extra can be modified freely, but currently only supports reading and displaying files under a fixed three-level directory
· The folder contains example files (Shanghai Metro)
· Folders with asterisks under static are required folders; if the main program is not modified, these folder names don't need to be changed
```

## Project Startup

```
· If the provided data is not in GCJ-02 coordinates, place the data in the Input folder according to its actual location
python trans_coordts.py
Results will be placed in the corresponding files under static/data following the Input format

· Run the program
python app.py
```
