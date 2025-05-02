import rasterio
import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
from rasterstats import zonal_stats
from rasterio.features import geometry_mask
from branca.colormap import linear
from pyproj import Proj

# ------------- TiffHandler Class -------------

class TiffHandler:
    def __init__(self, filepath):
        """
        Initialize TiffHandler with the provided TIF file path.
        """
        self.filepath = filepath
        self.dataset = rasterio.open(filepath)
        self.df = None  # DataFrame to store extracted data

    def extract_bands(self):
        """
        Extract all bands, compute vegetation indices, and return as a DataFrame.
        """
        if not self.dataset:
            raise ValueError("Dataset is not loaded. Please check the file path.")

        bands = [self.dataset.read(i) for i in range(1, self.dataset.count + 1)]
        band_stack = np.stack(bands, axis=-1)

        # Get pixel coordinates
        rows, cols = np.meshgrid(np.arange(band_stack.shape[0]), np.arange(band_stack.shape[1]), indexing='ij')
        xs, ys = rasterio.transform.xy(self.dataset.transform, rows, cols)

        flat_bands = band_stack.reshape(-1, band_stack.shape[2])
        flat_xs = np.array(xs).flatten()
        flat_ys = np.array(ys).flatten()

        # Band indices (adjust if your bands are ordered differently)
        red = flat_bands[:, 2].astype('float32')
        nir = flat_bands[:, 3].astype('float32')
        green = flat_bands[:, 1].astype('float32')
        blue = flat_bands[:, 0].astype('float32') if band_stack.shape[2] > 3 else np.zeros_like(red)

        # Vegetation indices
        ndvi = (nir - red) / (nir + red + 1e-10)
        gndvi = (nir - green) / (nir + green + 1e-10)
        savi = ((nir - red) / (nir + red + 0.5)) * (1.5)
        evi = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1 + 1e-10)

        # Construct DataFrame
        data = {
            'longitude': flat_xs,
            'latitude': flat_ys,
            'NDVI': ndvi,
            'GNDVI': gndvi,
            'SAVI': savi,
            'EVI': evi
        }

        # Add raw bands
        for i in range(band_stack.shape[2]):
            data[f'band_{i+1}'] = flat_bands[:, i]

        self.df = pd.DataFrame(data)
        return self.df
