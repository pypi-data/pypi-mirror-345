import folium
from folium.plugins import SideBySideLayers

class FoliumMap:
    def __init__(self, location, zoom_start=3, **kwargs):
        """
        Initializes a folium map centered at a given location with a specified zoom level.
        
        Parameters:
        location (tuple): Latitude and longitude coordinates for the map center.
        zoom_start (int): The initial zoom level of the map.
        """
        self.map = folium.Map(location=location, zoom_start=zoom_start, **kwargs)

    def add_basemap(self, basemap='OpenStreetMap'):
        """
        Adds a basemap to the folium map.
        
        Parameters:
        basemap (str): The name of the basemap to add (e.g., 'OpenStreetMap', 'Stamen Terrain', etc.).
        """
        basemaps = {
            'OpenStreetMap': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            'Stamen Terrain': 'http://{s}.tile.stamen.com/terrain/{z}/{x}/{y}.jpg',
            'Esri WorldImagery': 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
        }
        folium.TileLayer(tiles=basemaps.get(basemap, basemaps['OpenStreetMap']), attr=basemap).add_to(self.map)

    def add_layer_control(self):
        """
        Adds a layer control widget to the folium map for toggling layers.
        """
        folium.LayerControl().add_to(self.map)

    def add_vector(self, geo_data):
        """
        Adds vector data (GeoJSON or other formats supported by GeoPandas) to the map.
        
        Parameters:
        geo_data (GeoDataFrame or str): A GeoDataFrame or a path to a GeoJSON file.
        """
        if isinstance(geo_data, gpd.GeoDataFrame):
            geo_data = geo_data.to_json()
        folium.GeoJson(geo_data).add_to(self.map)
    
    def add_split_map(self, left_layer='OpenStreetMap', right_layer='Stamen Terrain'):
        """
        Adds a side-by-side split view of two different tile layers.
        
        Parameters:
        left_layer (str): Basemap name for the left side.
        right_layer (str): Basemap name for the right side.
        """
        # Define the basemap options
        basemaps = {
            'OpenStreetMap': folium.TileLayer(
                tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                name='OpenStreetMap', attr='OpenStreetMap'
            ),
            'Stamen Terrain': folium.TileLayer(
                tiles='http://{s}.tile.stamen.com/terrain/{z}/{x}/{y}.jpg',
                name='Stamen Terrain', attr='Stamen Terrain'
            ),
            'Esri WorldImagery': folium.TileLayer(
                tiles='http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                name='Esri WorldImagery', attr='Esri WorldImagery'
            )
        }

        # Get the left and right basemaps
        left = basemaps.get(left_layer, basemaps['OpenStreetMap'])
        right = basemaps.get(right_layer, basemaps['Stamen Terrain'])

        # Add the layers to the map
        left.add_to(self.map)
        right.add_to(self.map)

        # Add the side-by-side split functionality
        side_by_side = SideBySideLayers(left, right)
        side_by_side.add_to(self.map)

    def show_map(self):
        """
        Displays the folium map in the Jupyter notebook or Python script.
        """
        return self.map
