
# ------------- FoliumMap Class (folium) -------------

import folium
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib as mpl
from folium import TileLayer, LayerControl

class FoliumMap:
    def __init__(self, location, zoom_start=10):
        """
        Initialize a FoliumMap with a given location and zoom level.
        """
        self.map = folium.Map(location=location, zoom_start=zoom_start, control_scale=True)
        self.basemaps = {
            "OpenStreetMap": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "Esri.WorldImagery": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            "OpenTopoMap": "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
            "CartoDB.Positron": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
            "CartoDB.DarkMatter": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        }

    def add_basemap(self, name="OpenStreetMap"):
        """
        Adds a basemap layer to the map.
        """
        url = self.basemaps.get(name)
        if url:
            tile_layer = TileLayer(
                tiles=url,
                name=name,
                attr=name,
                overlay=False,
                control=True
            )
            tile_layer.add_to(self.map)
        else:
            print(f"Warning: Basemap '{name}' is not available.")

    def add_all_basemaps(self):
        """
        Adds all available basemaps as toggleable layers.
        """
        for name in self.basemaps:
            self.add_basemap(name)

    def add_vector(self, gdf, color_column, palette='YlGn', use_matplotlib=False, use_seaborn=False):
        """
        Adds vector data (GeoDataFrame) to the Folium map.
        Color the polygons based on a given column.
        """
        try:
            values = gdf[color_column]
            norm = plt.Normalize(vmin=values.min(), vmax=values.max())

            if use_seaborn:
                cmap = sns.color_palette(palette, as_cmap=True)
            else:
                cmap = plt.get_cmap(palette)

            colormap = [mpl.colors.rgb2hex(cmap(norm(i))) for i in np.linspace(values.min(), values.max(), 256)]

        except Exception as e:
            print(f"Warning: {e}. Using default 'YlGn' palette.")
            cmap = plt.get_cmap('YlGn')
            colormap = [mpl.colors.rgb2hex(cmap(i)) for i in np.linspace(0, 1, 256)]
            norm = plt.Normalize(vmin=values.min(), vmax=values.max())

        def style_function(feature):
            val = feature['properties'][color_column]
            idx = int(norm(val) * (len(colormap) - 1))
            idx = max(0, min(idx, len(colormap) - 1))
            return {
                'fillColor': colormap[idx],
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.7
            }

        geojson_data = gdf.to_json()

        folium.GeoJson(
            geojson_data,
            name="Vector Layer",
            style_function=style_function
        ).add_to(self.map)

    def add_layer_control(self):
        """
        Adds a layer control to the map.
        """
        LayerControl().add_to(self.map)

    def show(self):
        """
        Show the map.
        """
        return self.map
