# Imports
import folium
import webbrowser
import os

import pandas as pd
from shapely.geometry import Point, Polygon, MultiPolygon


def to_point(geom):
    """
    This function takes a shapley.geometry object and converts it to a Point object using the centroid.
    This is necessary to display the places more visually appealing on the maps by only showing the center points
    instead of the whole polygon or multipolygon.
    :param geom: A shapley.geometry object like Polygon or Multipolygon
    :return: Centroid of the geometry object
    """
    if isinstance(geom, (Polygon, MultiPolygon)):
        return Point(geom.centroid)
    else:
        return geom


class MapPlaces:
    """
    This class provides functionality to create an interactive map using the Folium library, visualize selected places
    from a DataFrame, and display the map in a web browser.
    :param df (pandas.DataFrame): A DataFrame containing information about places to be displayed on the map.
    :param coordinates (tuple): A tuple containing the latitude and longitude coordinates for the center of the map.
    :param map (folium.Map): A Folium map object initialized with the specified coordinates.

    Methods:
        get_imp_map(): Processes and adds relevant places to the map, grouping them by type and adding markers.
        show_map(filename: str): Saves the map to a file and opens it in the default web browser.
    """

    def __init__(self, df: pd.DataFrame, coordinates: list):
        """
        Initialize the MapPlaces object with a DataFrame and coordinates for the map center.
        :param df (pandas.DataFrame): A DataFrame containing information about places to be displayed on the map.
        :param coordinates (tuple): A tuple containing the latitude and longitude coordinates for the center of the map.
        """
        print("Map Places class has been loaded.")
        self.df, self.coordinates = df, coordinates
        self.map = folium.Map(location=coordinates, zoom_start=12)
        self.get_imp_map()

    def get_imp_map(self):
        """
        Process and add relevant places to the map, grouping them by type and adding markers with appropriate colors.
        The relevant places contain kindergarten, schools, residential and industrial areas.
        """
        # Select only relevant places
        imp = ['industrial', 'kindergarten', 'residential', 'school']
        places_imp = self.df[self.df['place'].isin(imp)]
        places_imp = places_imp.assign(geometry=places_imp['geometry'].apply(to_point))
        places_imp['lat'], places_imp['lon'] = places_imp.geometry.y, places_imp.geometry.x

        colors = {'industrial': 'blue', 'residential': 'green', 'kindergarten': 'red', 'school': 'orange'}
        # Iterate over the unique groups in the dataframe, create a feature for each group and create a marker for each
        # element in the group
        for group in places_imp['place'].unique():
            feature_group = folium.FeatureGroup(name=group)
            for index, row in places_imp[places_imp['place'] == group].iterrows():
                marker = folium.Marker(location=[row['lat'], row['lon']], tooltip=row['place'],
                                       icon=folium.Icon(color=colors[group]))
                marker.add_to(feature_group)
            feature_group.add_to(self.map)
        folium.LayerControl().add_to(self.map)

    def show_map(self, filename: str):
        """
        Save the map to a file and open it in the default web browser.
        :param filename: The name of the HTML file as a string to which the map will be saved.
        """
        self.map.save(filename)
        webbrowser.open('file://' + os.path.realpath(filename))
