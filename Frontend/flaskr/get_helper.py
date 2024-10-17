# Imports
from datetime import datetime, date, time, timedelta
from typing import List, Union, Any
from flask import flash
import networkx as nx
import osmnx as ox
import folium
import folium.plugins as plugins


class Functionalities:
    """
    This class provides various utility functions for working with location data and creating maps.
    """

    @staticmethod
    def time_filter(locations: List[dict], selected_date: date, selected_time: time, route: bool = False):
        """
        This method filters a list of locations based on the selected date and time.
        :param locations: A list of dictionaries representing locations to be filtered.
        :param selected_date: The selected date for filtering.
        :param selected_time: The selected time for filtering.
        :param route: A boolean indicating whether the filtering is for a route (default: False).
        :return: A filtered list of locations based on the selected date and time.
        """

        # Date and time are selected / Time only selected (date tomorrow)
        if selected_date != "" and selected_time != "":
            selected_timestamp_from = datetime.combine(selected_date, selected_time).replace(second=0)
            # For the shortest paths on the deliverer_routesite
            if route:
                selected_timestamp_to = selected_timestamp_from + timedelta(hours=2)
                locations = list(filter(lambda loc: loc["timestamp_from"] >= selected_timestamp_from, locations))
                locations = list(filter(lambda loc: loc["timestamp_from"] <= selected_timestamp_to, locations))
            else:
                locations = list(filter(lambda loc: loc["timestamp_from"] == selected_timestamp_from, locations))

        # Only date is selected
        elif selected_date != "":
            selected_timestamp_from = selected_date
            locations = list(filter(lambda loc: datetime.date(loc["timestamp_from"]) == selected_timestamp_from,
                                    locations))
        
        # Flash selected filters to user
        if route and selected_time != "":
            flash_message = 'from ' + str(selected_timestamp_from) + ' until ' + str(selected_timestamp_to)
        else:
            flash_message = str(selected_timestamp_from)

        return locations, flash_message

    @staticmethod
    def get_nearest_node(coords: tuple):
        """
        This method takes a (lat, lon) coordinate tuple and returns the nearest node in the bike network. 
        It first tries to map it within a distance of 100 meters max., but the exception handles cases where
        this is not possible (might result in not precise visualisation).
        :param coords: A (lat, lon) coordinate tuple
        :return: The nearest node of the coordinate in the bike network
        """
        try:
            graph = ox.graph_from_point(coords, dist=100, network_type="bike")
        except (nx.NetworkXPointlessConcept, ValueError):
            graph = ox.graph_from_point(coords, dist=200, network_type="bike")
        nearest_node = ox.distance.nearest_nodes(graph, coords[0], coords[1])
        return nearest_node

    @staticmethod
    def get_shortest_path(graph: nx.MultiDiGraph, start_node: int, end_node: int, weight: str):
        # This function takes a graph and two nodes and returns the length of the shortest path between them
        """
        This method takes a (lat, lon) coordinate tuple and returns the nearest node in the bike network.
        :param graph: A networkx graph of the chosen city
        :param start_node: A networkx node where the shortest path should start from
        :param end_node: A networkx node where the shortest path should end at
        :param weight: A string with the weight for the shortest path.
        :return: The method returns the shortest path between the given nodes in the given graph.
        Also, it returns its length and duration.
        """
        route = nx.shortest_path(graph, start_node, end_node, weight=weight)
        route_length = nx.shortest_path_length(graph, start_node, end_node, weight='length')
        route_duration = nx.shortest_path_length(graph, start_node, end_node, weight='travel_time')

        return route, route_length, route_duration

    @staticmethod
    def add_map(locations: list[dict[str, Union[str, Any]]], tooltips: str,
                icon_configs: list[dict[str, str]], capacities: dict = False,
                popup: bool = False, polylines: bool = False, shortest_paths: list = None,
                graph: nx.MultiDiGraph = None):
        """
        This method adds a map to the current instance of Functionalities.
        param locations: A list of dictionaries containing location information.
        :param tooltips: Tooltip text for map markers.
        :param icon_configs: A list of dictionaries containing icon configuration for markers.
        :param capacities: A dictionary of capacities (optional).
        :param popup: Whether to include a popup for markers (optional).
        :param polylines: Whether to include polylines on the map (optional).
        :param shortest_paths: A list of shortest paths (optional).
        :param graph: A MultiDiGraph object representing the graph (optional).
        :return: The map object.
        """

        # Initialise map object and colors    
        city_map = folium.Map(location=[48.791664762923176, 9.177939808094296], zoom_start=11)
        markercolors = {1: '#c24a4a', 2: '#4AC2A4', 3: '#c28c4a', 4: '#c24a9c', 5: '#4a54c2'}

        coordinates = {}

        for i, location in enumerate(locations):
            
            latitude = location['latitude']
            longitude = location['longitude']
            station_id = location['station_id']
            todays_date = location['timestamp_from'].date()

            capacity = capacities[(station_id, todays_date)]

            # Get tooltip configurations
            tooltip = tooltips.format(station_id=station_id, capacity=capacity)
            icon_config = icon_configs[i]
            icon = plugins.BeautifyIcon(**icon_config)

            # Routesite configurations
            if polylines:
                # Make a list of the coordinates of the station for plotting the routes
                if station_id not in coordinates:
                    coordinates[station_id] = []
                coordinates[station_id].append((latitude, longitude))
            
            # Driversite configurations
            if shortest_paths is not None:
                if i == 0:
                    city_map = ox.plot_route_folium(graph, shortest_paths[i], popup_attribute="length", weight=7,
                                                    color=markercolors[station_id], zoom_start=10)
                elif i < (len(locations)-1):
                    city_map = ox.plot_route_folium(graph, shortest_paths[i], route_map=city_map,
                                                    popup_attribute="length", weight=7, color=markercolors[station_id],
                                                    zoom_start=10)
            
            # Add markers
            marker = folium.Marker(
                location=[latitude, longitude],
                icon=icon,
                tooltip=tooltip,  
            )
            if popup:
                popup = '<button onclick="$.post(\'/save_coords\', {\'lat\':' + str(latitude) + ', \'lng\': ' +\
                        str(longitude)+', \'station_id\': ' + str(station_id)+', \'date\': \''+str(todays_date) +\
                        '\', \'capacity\': \'' + str(capacity) + '\'});">Select station</button>'
                marker.add_child(folium.Popup(popup))
            marker.add_to(city_map)

        # Polylines
        if polylines:
            for station_id, coords in coordinates.items():
                polyline_coordinates = [(float(lat), float(lon)) for lat, lon in coords]
                
                folium.PolyLine(
                    locations=polyline_coordinates,
                    color=markercolors[station_id],
                    weight=2,  
                    opacity=0.8  
                ).add_to(city_map)
        
        return city_map
            
