
# ------------- ShapefileHandler Class -------------
import geopandas as gpd
import numpy as np
from rasterstats import zonal_stats

class ShapefileHandler:
    def __init__(self, shapefile_path):
        """
        Initialize ShapefileHandler with the provided shapefile path.
        """
        self.shapefile_path = shapefile_path
        self.gdf = gpd.read_file(shapefile_path)
        
        # Ensure geometries are valid
        self.gdf['valid'] = self.gdf.is_valid
        self.gdf['geometry'] = self.gdf['geometry'].buffer(0)
        
        # Filter for valid polygons only
        self.gdf = self.gdf[self.gdf.geom_type == 'Polygon']
    
    def get_shapefile_data(self):
        """
        Returns the loaded GeoDataFrame.
        """
        return self.gdf

