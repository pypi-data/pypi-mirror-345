# Welcome to agrihealth


[![image](https://img.shields.io/pypi/v/agrihealth.svg)](https://pypi.python.org/pypi/agrihealth)


**agrihealth is a Python package that allows fa**


-   Free software: MIT License
-   Documentation: <https://terra-geo.github.io/agrihealth>
    

# **Overview** 

**agrihealth** is a demo Python package designed for **farmers, foresters, and environmental researchers** to analyze **vegetation health** and **soil moisture** using satellite imagery. The package enables **offline processing**, making it ideal for remote areas with limited internet access.  


### How to install agrihealth

``` python
pip install agrihealth
```

## **Key Features**  

### **Vegetation Index Computation**  
**agrihealth** allows users to compute key vegetation indices for monitoring plant health and ecosystem conditions:  

- **NDVI (Normalized Difference Vegetation Index)**  
  - Evaluates plant health by measuring chlorophyll content.  
- **SAVI (Soil-Adjusted Vegetation Index)**  
  - Adjusts for soil brightness in sparse vegetation areas.  
- **EVI (Enhanced Vegetation Index)**  
  - Enhances vegetation sensitivity by reducing atmospheric effects.  
- **SMI (Soil Moisture Index)**  
  - Estimates soil moisture content to assess water availability for crops.  

### **Offline Processing**  
- Perform all computations locally without needing an internet connection.  
- Ideal for field applications where internet access is limited.  

### **Multi-Source Satellite Imagery Support**  
Compatible with images from:  

- **Landsat (NASA/USGS)**  
- **Sentinel-2 (ESA)**  
- **MODIS (NASA)**  
- Other remote sensing datasets.  

### **Easy-to-Use**  
Simple Python functions to:  

- Load satellite data.  
- Compute vegetation and soil moisture indices.  
- Visualize results with minimal coding effort.  

### **Customizable Analysis**  
Users can fine-tune parameters based on:  

- Different climate conditions.  
- Soil types.  
- Vegetation structures.  

### **Visualization & Data Export**  
Generate heatmaps and overlay indices on satellite images.  
Export results in multiple formats:  

- **GeoTIFF** for GIS applications.  
- **PNG** for quick visualization.  
- **CSV** for further statistical analysis.  
