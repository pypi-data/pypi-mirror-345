from ipyleaflet import ImageOverlay

class ImageOverlayManager:
    def __init__(self, map_object):
        self.map = map_object

    def add_image(self, url, bounds, opacity=1.0):
        """
        Add an image or animated GIF overlay to the map.

        Parameters:
        - url (str): Image or GIF URL
        - bounds (tuple): ((south, west), (north, east))
        - opacity (float): 0.0 to 1.0
        """
        image = ImageOverlay(
            url=url,
            bounds=bounds,
            opacity=opacity
        )
        self.map.add_layer(image)
