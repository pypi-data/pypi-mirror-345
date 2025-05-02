
# ------------- LeafletMap Class (ipyleaflet) -------------

import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import json
import geopandas as gpd
from ipyleaflet import Map, basemaps, basemap_to_tiles, LayersControl, GeoJSON
from ipywidgets import VBox


class LeafletMap:
    def __init__(self, center=(0, 0), zoom=10):
        self.center = center
        self.zoom = zoom
        self.map = Map(center=self.center, zoom=self.zoom)

        self.available_basemaps = {
            "OpenStreetMap": "OpenStreetMap.Mapnik",
            "Esri World Imagery": "Esri.WorldImagery",
            "DEM (OpenTopoMap)": "OpenTopoMap"
        }

        self.add_basemaps()
        self.map.add_control(LayersControl(position='topright'))

    def resolve_basemap(self, path_str):
        """Resolve a dotted path string to a basemap object from ipyleaflet.basemaps"""
        obj = basemaps
        for part in path_str.split('.'):
            obj = obj[part]
        return obj

    def add_basemaps(self):
        """Add selected basemap layers to the map"""
        first_layer = True
        for name, path in self.available_basemaps.items():
            try:
                basemap_config = self.resolve_basemap(path)
                layer = basemap_to_tiles(basemap_config)
                layer.name = name
                if first_layer:
                    self.map.layers = (layer,)
                    first_layer = False
                else:
                    self.map.add_layer(layer)
            except Exception as e:
                print(f"[Warning] Could not load basemap '{name}': {e}")

        
    def add_vector(self, gdf, color_column, palette='YlGn'):
        """
        Add a vector layer (GeoJSON) to the map with color styling.
        """
        values = gdf[color_column]
        norm = plt.Normalize(vmin=values.min(), vmax=values.max())
        cmap = plt.get_cmap(palette)

        def get_color(val):
            return mpl.colors.rgb2hex(cmap(norm(val)))

        geojson_data = json.loads(gdf.to_json())
        for feature in geojson_data['features']:
            val = feature['properties'][color_column]
            feature['properties']['style'] = {
                'color': 'black',
                'weight': 0.5,
                'fillColor': get_color(val),
                'fillOpacity': 0.7
            }

        geojson_layer = GeoJSON(data=geojson_data, name="Vector Layer")
        self.map.add_layer(geojson_layer)

    def show(self):
        return VBox([self.map])