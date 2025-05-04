
# ------------- LeafletMap Class (ipyleaflet) -------------

import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import geopandas as gpd
import ipyleaflet
from ipyleaflet import basemaps, LayersControl, GeoJSON, Map
from ipywidgets import VBox

class LeafletMap(ipyleaflet.Map):
    def __init__(self, center=(20, 0), zoom=10, height="500px" ,**kwargs):
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height
        self.scroll_wheel_zoom=True

    def add_basemap(self, basemap="OpenStreetMap"):
        basemaps = {
            "OpenStreetMap": {
                "url": 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                "attribution": 'OpenStreetMap'
            },
            "OpenTopoMap": {
                "url": 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
                "attribution": 'OpenTopoMap'
            },
            "Esri Satellite": {
                "url": 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                "attribution": 'ESRI'
            }
        }
        
        try:
            basemap_layer = basemaps[basemap]
            self.add_layer(ipyleaflet.TileLayer(url=basemap_layer["url"], attribution=basemap_layer["attribution"]))
        except KeyError:
            print(f"Basemap '{basemap}' not found. Using 'OpenStreetMap' instead.")
            self.add_layer(ipyleaflet.TileLayer(url=basemaps["OpenStreetMap"]["url"], attribution=basemaps["OpenStreetMap"]["attribution"]))

    def add_geojson(self, 
                    data, 
                    zoom_to_layer = True,
                    hover_style = {"color":"blue", "fillOpacity":0.5}, 
                    **kwargs,
    ):
        gdf = gpd.read_file(data)
        geojson = gdf.__geo_interface__
        gj = GeoJSON(data=geojson, hover_style = hover_style, **kwargs)
        self.add_layer(gj)

        if zoom_to_layer:
            bounds = gdf.total_bounds
            self.fit_bounds([[bounds[1], bounds[0], bounds[3], bounds[2]]])

    def add_shp(self, data, **kwargs):
        
        gdf = gpd.read_file(data)
        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__
        self.add_geojson(geojson, **kwargs)