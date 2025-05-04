# AgriHealth - Usage Guide

AgriHealth is a Python package designed to simplify vegetation index analysis using remote sensing imagery (e.g., satellite or drone imagery) and GIS shapefiles. This guide walks you through the core components of the package.

---
# FoliumMap User Documentation

## Introduction

The `FoliumMap` class is a powerful tool for creating interactive maps with various basemaps and data layers. This documentation provides a step-by-step guide on how to use the `FoliumMap` class to create your own maps.

## Getting Started

### Installation

To use the `FoliumMap` class, you'll need to have the following installed:

* `folium`
* `geopandas`

You can install these libraries using pip:

```bash
pip install folium geopandas
```

## Creating a Map

To create a map, you'll need to initialize a `FoliumMap` object with the desired center coordinates, zoom start level, and height. Here's an example:

```python
m = FoliumMap(center=(-12.6814, -55.4853), zoom_start=6, height=600)
```

## Adding Basemaps

The `FoliumMap` class supports several basemaps, including:

* OpenStreetMap
* OpenTopoMap
* Esri Satellite

You can add a basemap to your map using the `add_basemap` method:

```python
m.add_basemap("OpenStreetMap")
```

## Adding Data Layers

The `FoliumMap` class supports adding GeoJSON files and shapefiles as data layers. Here's an example of how to add a GeoJSON file:

```python
m.add_geojson("path_to_your_geojson_file.geojson")
```

And here's an example of how to add a shapefile:

```python
m.add_shp("path_to_your_shapefile.shp")
```

## Saving the Map

Once you've added your basemap and data layers, you can save the map as an HTML file using the `save` method:

```python
m.save("map.html")
```

## Tips and Tricks

* Make sure to replace `"path_to_your_geojson_file.geojson"` and `"path_to_your_shapefile.shp"` with the actual paths to your files.
* You can customize the appearance of your map by passing additional keyword arguments to the `FoliumMap` constructor and the `add_geojson` and `add_shp` methods.

## Troubleshooting

If you encounter any issues while using the `FoliumMap` class, make sure to check the following:

* That you have the required libraries installed.
* That your GeoJSON file or shapefile is in the correct format.
* That you've specified the correct path to your GeoJSON file or shapefile.

By following these steps and tips, you should be able to create your own interactive maps using the `FoliumMap` class.
---

For more details, check the full documentation or explore example notebooks.