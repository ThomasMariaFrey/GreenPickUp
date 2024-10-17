"""
This class creates the overall dataframe structure with cell polygons
"""
import numpy as np
import osmnx as ox
import geopandas as gpd
import folium
import os
import webbrowser
from shapely.geometry import Polygon


class Dataframe:
    """
    This class initializes the dataframe structure from scratch
    :param city: The city of interest. This is important because the shapely.geometry objects of the grid cells
    need to have their corresponding coordinates
    :param cells_lat, cells_lon: The number of cells in latitude and longitude to form the records of the dataframe
    """
    def __init__(self, city: str, cells_lat: int, cells_lon: int):
        print("Initialize Dataframe class has been loaded.")
        # initialize all elements
        self.city, self.cells_lat, self.cells_lon = city, cells_lat, cells_lon
        self.max_lat = self.min_lat = self.max_lon = self.min_lon = self.data_gdf = None
        # The method initialize() is executed in the main file to return the dataframe directly in the main file and
        # not a Dataframe object in order to pipeline the dataframe to the next class.

    def initialize(self):
        # take the extreme coordinates of the city and obtain the box coordinates. The box forms the extreme
        # coordinates of the whole grid
        self.max_lat, self.min_lat, self.max_lon, self.min_lon = tuple(
            ox.geocode_to_gdf(self.city)[["bbox_north", "bbox_south", "bbox_east", "bbox_west"]].iloc[0])
        box_lat = np.linspace(self.min_lat, self.max_lat, self.cells_lat + 1)
        box_lon = np.linspace(self.max_lon, self.min_lon, self.cells_lon + 1)
        # create the single grid cells as polygons
        polygon_list = []
        for i in range(len(box_lat) - 1):
            for j in range(len(box_lon) - 1):
                polygon_list.append(Polygon([[box_lon[j], box_lat[i + 1]], [box_lon[j + 1], box_lat[i + 1]],
                                             [box_lon[j + 1], box_lat[i]], [box_lon[j], box_lat[i]]]))
        # create a geopandas dataframe with ids and the polygons as attributes
        self.data_gdf = gpd.GeoDataFrame({"cell_id": list(range(0, self.cells_lat * self.cells_lon)),
                                          "geometry": polygon_list})
        # return the geopandas dataframe
        return self.data_gdf

    def display_folium_map(self, data: gpd.GeoDataFrame):
        """
        This function plots a folium visualization of the complete grid with the cell polygons
        :param data: The geopandas dataframe
        :return: A folium map of the grid cells. This plot is saved as an .html file and offers the usual zoom function
        """
        # Create a folium map with the city centre
        m = folium.Map(location=[(self.max_lat + self.min_lat) / 2, (self.max_lon + self.min_lon) / 2], zoom_start=17)
        # For each polygon, add it as a geojson object to the folium map
        for _, r in data.iterrows():
            geo_j = gpd.GeoSeries(r["geometry"]).to_json()
            geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {"fillColor": "orange"})
            folium.Popup(r["cell_id"]).add_to(geo_j)
            geo_j.add_to(m)
        filename = "cells_folium.html"
        m.save(filename)
        webbrowser.open("file://" + os.path.realpath(filename))

    def save_csv(self, data: gpd.GeoDataFrame, name: str):
        data.to_csv(name)
