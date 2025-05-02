# agrihealth/__init__.py

__author__="""M Fisher"""
__email__="climatealerta@gmail.com"
__version__="0.0.2"

"""
Initialization file for the agrihealth package.

Exposes:
- core module (with TiffHandler,ShapefileHandler, LeafletMap, FoliumMap classes)
"""


from .core import TiffHandler, LeafletMap, FoliumMap, ShapefileHandler

__all__ = [
    "TiffHandler",
    "ShapefileHandler",
    "LeafletMap",
    "FoliumMap"
]
