
# ------------- FoliumMap Class (folium) -------------

import folium
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib as mpl
import json
from folium import TileLayer, LayerControl
import geopandas as gpd

class FoliumMap(folium.Map):
    
    def __init__(self, center=(20, 0), zoom_start=10, height=500, **kwargs):
        super().__init__(location=center, zoom_start=zoom_start, height=height, **kwargs)

    def add_basemap(self, basemap="OpenStreetMap"):
        if basemap == "OpenStreetMap":
            folium.TileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', 
                            attr='Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors').add_to(self)
        elif basemap == "OpenTopoMap":
            folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', 
                            attr='Map data: &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)').add_to(self)
        elif basemap == "Esri Satellite":
            folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 
                            attr='&copy; <a href="https://www.esri.com/">ESRI</a>').add_to(self)
        else:
            raise ValueError("Unsupported basemap")

    def add_geojson(self, data, zoom_to_layer=True, hover_text=None, **kwargs):
        if isinstance(data, str):
            gdf = gpd.read_file(data)
        else:
            gdf = gpd.GeoDataFrame.from_features(data)
        
        geojson = json.loads(gdf.to_json())
        folium.GeoJson(geojson, name='geojson', **kwargs).add_to(self)

        if zoom_to_layer:
            bounds = gdf.total_bounds
            self.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    def add_shp(self, data, **kwargs):
        gdf = gpd.read_file(data)
        gdf = gdf.to_crs(epsg=4326)
        self.add_geojson(gdf.__geo_interface__, **kwargs)

