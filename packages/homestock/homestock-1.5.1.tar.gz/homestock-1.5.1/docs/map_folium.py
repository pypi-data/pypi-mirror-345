# homestock module

import folium
import geopandas as gpd
import os


class Map:
    """
    A custom folium-based map class for the homestock package,
    supporting basemaps, layer control, and vector data visualization.
    """

    def __init__(self, location=(0, 0), zoom_start=2):
        """
        Initialize the Map.

        Parameters:
        ----------
        location : tuple
            Center of the map in (lat, lon).
        zoom_start : int
            Initial zoom level.
        """
        self.map = folium.Map(location=location, zoom_start=zoom_start)
        self._layers = []

    def add_basemap(self, basemap_name: str):
        """
        Add a basemap to the map.

        Parameters:
        ----------
        basemap_name : str
            Name of the basemap. Supported values:
            "OpenStreetMap", "Esri.WorldImagery", "OpenTopoMap".

        Returns:
        -------
        None
        """
        tile_dict = {
            "OpenStreetMap": "OpenStreetMap",
            "Esri.WorldImagery": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            "OpenTopoMap": "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        }

        attr_dict = {
            "Esri.WorldImagery": "Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye",
            "OpenTopoMap": "© OpenTopoMap (CC-BY-SA)",
        }

        if basemap_name not in tile_dict:
            raise ValueError(f"Unsupported basemap '{basemap_name}'.")

        tile_url = tile_dict[basemap_name]
        attr = attr_dict.get(basemap_name, basemap_name)

        tile_layer = folium.TileLayer(tiles=tile_url, attr=attr, name=basemap_name)
        tile_layer.add_to(self.map)
        self._layers.append(tile_layer)

    def add_layer_control(self):
        """
        Add a layer control widget to the map.

        Returns:
        -------
        None
        """
        folium.LayerControl().add_to(self.map)

    def add_vector(self, data, layer_name="Vector Layer"):
        """
        Add vector data to the map. Accepts file paths or GeoDataFrames.

        Parameters:
        ----------
        data : str or geopandas.GeoDataFrame
            Path to the vector data file or a GeoDataFrame.
        layer_name : str
            Name of the layer to display.

        Returns:
        -------
        None
        """
        if isinstance(data, str):
            if not os.path.exists(data):
                raise FileNotFoundError(f"File '{data}' not found.")
            gdf = gpd.read_file(data)
        elif isinstance(data, gpd.GeoDataFrame):
            gdf = data
        else:
            raise TypeError("Data must be a file path or a GeoDataFrame.")

        geojson = folium.GeoJson(gdf, name=layer_name)
        geojson.add_to(self.map)
        self._layers.append(geojson)

    def display(self):
        """
        Return the folium map object for display in Jupyter.

        Returns:
        -------
        folium.Map
        """
        return self.map
