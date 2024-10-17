"""
This class does the route planning: It takes the locations of the RL algorithm as a dataframe, optimizes the routes
and provides the result both numerically as a list of routes and visually as a folium map to be integrated into the
frontend.
"""
import osmnx as ox
import networkx as nx
import pandas as pd
import itertools
import folium
import ast
import webbrowser
import os


def get_nearest_node(coords: tuple):
    # This function takes a (lat, lon) coordinate tuple and returns the nearest node in the bike network
    try:
        graph = ox.graph_from_point(coords, dist=100, network_type="bike")
    # To reduce runtime, search for the nearest node in a distance of 100 meters. If there is no node within this
    # distance, go for the 200 meters
    # We take the bike network because the routes are supposed to be drive by the parcel delivery drivers on electric
    # bikes
    except (nx.NetworkXPointlessConcept, ValueError):
        graph = ox.graph_from_point(coords, dist=200, network_type="bike")
    nearest_node = ox.distance.nearest_nodes(graph, coords[0], coords[1])
    return nearest_node


def shortest_path(graph: nx.MultiDiGraph, start_node: int, end_node: int):
    # This function takes a graph and two nodes and returns the length of the shortest path between them
    route = nx.shortest_path(graph, start_node, end_node, weight="length")
    route_length = int(sum(ox.utils_graph.get_route_edge_attributes(graph, route, "length")))
    return route_length


def create_subroutes(graph: nx.MultiDiGraph, sorted_start_nodes: list, sorted_end_nodes: list):
    """
    This function takes source nodes and end nodes and returns matches of tuples which minimize the joint distance
    that needs to be driven to connect all points from the source nodes with all points from the target nodes
    :param graph: the networkx graph over which the routes are going to be calculated
    :param sorted_start_nodes: a list of start nodes
    :param sorted_end_nodes: a list of target nodes
    :return: a list of tuples of which each tuple contains one source node and one target node
    """
    # Calculate all mutual distances between start nodes and end nodes
    # The result is a dictionary of length n^2 with all node combinations as key and their distance as value
    combinations_list = [[start_node, end_node] for start_node in sorted_start_nodes for end_node in
                         sorted_end_nodes]
    distances_dict = {tuple(nodes_pair): shortest_path(graph, nodes_pair[0], nodes_pair[1]) for nodes_pair in
                      combinations_list}

    # Calculate all feasible routes. Fix the starting nodes. Permutate over all combinations of the ending nodes and
    # match them with the starting nodes. This results in n! possible route combinations
    # The result is a list which contains n! route combinations. Each element of the list,
    # i.e., a route combination, consists of a list of n 2-tuples, matching start nodes with end nodes
    feasible_routes = []
    end_node_permutations = list(itertools.permutations(sorted_end_nodes))
    for end_node_permutation in end_node_permutations:
        route = list(zip(sorted_start_nodes, end_node_permutation))
        feasible_routes.append(route)

    # For each of the feasible routes, compute its joint distance
    # Create a list of length n! with the corresponding joint distance of the feasible routes
    # Distances are extracted from the dictionary above
    route_distances = []
    for routes in feasible_routes:
        distance = 0
        for route in routes:
            distance += distances_dict[route]
        route_distances.append(distance)

    # Obtain the minimum joint distance and its corresponding routes
    shortest_routes = feasible_routes[route_distances.index(min(route_distances))]
    return shortest_routes


def merge_subroutes(first_routes: list, second_routes: list):
    # This function takes two lists of tuples with routes, concatenates them and
    # returns a list of tuples with each tuple having more elements
    sorted_first_routes = sorted(first_routes, key=lambda x: x[-1])
    sorted_second_routes = sorted(second_routes, key=lambda x: x[0])
    # Check that the routes can be concatenated
    assert [t[-1] for t in sorted_first_routes] == [t[0] for t in sorted_second_routes],\
        "Error: Routes does not match after each other and cannot be concatenated"
    # Finally concatenate them together
    concatenated_routes = [tuple1 + tuple2[1:] for tuple1, tuple2 in zip(sorted_first_routes, sorted_second_routes)]
    return concatenated_routes


def add_depot(depot: tuple, routes: list):
    # This function adds the depot as the first place in the morning and the last place in the evening to the route
    if depot is not None:
        depot_node = get_nearest_node(depot)
        routes = [(depot_node, ) + route + (depot_node, ) for route in routes]
    return routes


def get_locations_dict(data: pd.DataFrame, column_name: str):
    # This function takes the dataframe of locations and transforms it into a dictionary for further processing
    # The column with the time point becomes the key and all actions become a list as value
    locations = {}
    for _, row in data.iterrows():
        key = row[column_name]
        values = row.drop(column_name).tolist()
        locations[key] = values
    # Manipulations to clean the data in the locations dictionary
    # If the values within the columns are strings, convert them back to numbers
    if isinstance(list(locations.values())[1][0], str):
        locations = {key: [ast.literal_eval(string) for string in value] for key, value in locations.items()}
    # Convert the coordinates which are passed from the RL actions into their nearest nodes in the network
    locations = {key: [get_nearest_node(sublist) for sublist in value] for key, value in locations.items()}
    # Sort them for a deterministic output and to pass them into create_subroutes() which require a sorted input
    locations = {key: sorted(value) for key, value in locations.items()}
    return locations


class RoutePlanning:
    """
    This class takes a dataframe with the actions from the RL algorithm and creates the routes to be driven to get
    from station to station
    :param city: The city of interest. This is important because we need the network graph of the city
    :param locations: The dataframe with the actions. The first column contains the time at which the stations are to
    be moved and all subsequent columns contain the coordinates of the positions at where the stations are to be located
    :param depot: The tuple of the coordinates of the central depot at which all stations start in the morning and
    end in the evening
    :param weight: "length" or "duration". If the routes shall be determined by length or duration
    """
    def __init__(self, city: str, locations: pd.DataFrame, depot: tuple = None, weight: str = "length"):
        print("Route Planning class has been loaded.")
        # Initialize all elements
        self.city, self.locations, self.depot, self.weight = city, locations, depot, weight
        self.G = ox.graph_from_place(self.city, network_type="bike")
        # Finally get the routes
        self.routes = self.create_routes()

    def create_routes(self):
        # This function combines all steps to return routes as a list of tuples from the locations dataframe
        # First, get a dictionary out of the locations dataframe. The column with the time is named "DataSet"
        self.locations = get_locations_dict(self.locations, "DataSet")
        # Obtain all keys of the dictionary as local variables with their values as values
        locals().update(self.locations)
        # List all keys, i.e., how many stations are in the data
        locations_keys = list(self.locations.keys())
        # Iterate over all start nodes, subsequently concatenate the next nodes until the final route is built
        for index, element in enumerate(self.locations.keys()):
            if index == 0:
                continue
            elif index == 1:
                subroutes_zero = create_subroutes(self.G, self.locations[locations_keys[index-1]],
                                                  self.locations[locations_keys[index]])
            elif index == 2:
                subroutes = create_subroutes(self.G, self.locations[locations_keys[index-1]],
                                             self.locations[locations_keys[index]])
                self.routes = merge_subroutes(subroutes_zero, subroutes)
            else:
                subroutes = create_subroutes(self.G, self.locations[locations_keys[index-1]],
                                             self.locations[locations_keys[index]])
                self.routes = merge_subroutes(self.routes, subroutes)
        # Add a depot if a depot is passed
        self.routes = add_depot(self.depot, self.routes)
        return self.routes

    def get_routes(self):
        return self.routes  # Return the routes for the purpose of testing

    def plot_routes_osmnx(self):
        """
        This function plots a networkx graph of the city of interest and highlights the routes in it.
        The output is not saved.
        """
        routes_list = []
        color_list = []
        for index, route in enumerate(self.routes):
            for i in range(len(route)):
                routes_list.append(nx.shortest_path(self.G, route[i - 1], route[i], weight=self.weight))
                color_list.append(index)
        color_map = {0: "red", 1: "blue", 2: "green", 3: "yellow", 4: "magenta", 5: "brown", 6: "lime",
                     7: "darkviolet", 8: "darkorange", 9: "mediumblue", 10: "darkred", 11: "darkgreen"}
        color_list = [color_map[c] for c in color_list]
        ox.plot_graph_routes(self.G, routes_list, route_colors=color_list, node_size=4)

    def plot_routes_folium(self, filename: str):
        """
        This function plots a folium map of the routes and adds markers at where the stations are located
        """
        # This block is only a preparation to create the folium map
        nodes = self.G.nodes
        node_coordinates = [(nodes[node]["y"], nodes[node]["x"]) for node in nodes]
        node_coordinates_lat = [node_coordinate[0] for node_coordinate in node_coordinates]
        node_coordinates_lon = [node_coordinate[1] for node_coordinate in node_coordinates]
        center_lat = (min(node_coordinates_lat) + max(node_coordinates_lat)) / 2
        center_lon = (min(node_coordinates_lon) + max(node_coordinates_lon)) / 2
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11)

        color_map = {0: "red", 1: "blue", 2: "green", 3: "orange", 4: "purple", 5: "lightgreen", 6: "pink",
                     7: "lightred", 8: "darkblue", 9: "darkred", 10: "darkgreen", 11: "beige"}
        # This block subsequently adds markers and routes to the plot
        for index, route in enumerate(self.routes):
            route_coordinates = []
            for index2, element in enumerate(route):
                coords = (self.G.nodes[element]["y"], self.G.nodes[element]["x"])
                folium.Marker(location=coords, icon=folium.Icon(color=color_map[index], icon=str(index2+1),
                                                                prefix="fa")).add_to(m)
                route_coordinates.append(coords)
                if index2 > 0:
                    path = nx.shortest_path(self.G, route[index2-1], element, weight=self.weight)
                    if len(path) > 1:
                        m = ox.plot_route_folium(self.G, path, route_map=m, popup_attribute="length",
                                                 weight=3, color=color_map[index])
        m.save(filename)
        webbrowser.open("file://" + os.path.realpath(filename))
