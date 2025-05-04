from ipyleaflet import VideoOverlay

class VideoOverlayManager:
    def __init__(self, map_object):
        self.map = map_object

    def add_video(self, url, bounds, opacity=1.0):
        """
        Add a video overlay to the map.

        Parameters:
        - url (str or list): Video file URL(s)
        - bounds (tuple): ((south, west), (north, east))
        - opacity (float): 0.0 to 1.0
        """
        video = VideoOverlay(
            url=url,
            bounds=bounds,
            opacity=opacity
        )
        self.map.add_layer(video)
