from ipyleaflet import WMSLayer

class WMSLayerManager:
    def __init__(self, map_object):
        self.map = map_object

    def add_wms_layer(self, url, layers, name="WMS Layer", format="image/png", transparent=True, **kwargs):
        """
        Add a WMS layer to the map.

        Parameters:
        - url (str): WMS service endpoint
        - layers (str): Comma-separated list of layer names
        - name (str): Display name
        - format (str): Format type like 'image/png'
        - transparent (bool): Layer transparency
        - kwargs: Optional WMS parameters
        """
        wms = WMSLayer(
            url=url,
            layers=layers,
            name=name,
            format=format,
            transparent=transparent,
            **kwargs
        )
        self.map.add_layer(wms)
