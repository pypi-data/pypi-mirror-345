from setuptools import setup, find_packages

setup(
    name="agrihealth",
    version="0.0.3",
    author="Your Name",
    author_email="climatealerta@gmail.com",
    description="A package for computing vegetation and soil moisture indices using satellite imagery.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/terra-geo/agrihealth",  
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "matplotlib",
        "rasterio",
        "folium",
        "ipyleaflet",
        "pandas",
        "geopandas",  # to use shapefiles
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
