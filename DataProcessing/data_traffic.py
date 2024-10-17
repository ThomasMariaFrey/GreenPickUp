"""
This function takes a dataframe and updates or creates a traffic attribute
"""
import geopandas as gpd
import matplotlib.pyplot as plt
import osmnx as ox
import networkx as nx
import random
import os
import webbrowser
from shapely.geometry import Point


class TrafficDataframe:
    """
    This class takes a dataframe and updates or creates a traffic attribute
    :param data: The dataframe to be updated with the traffic attribute. If a traffic attribute is not yet persistent
    in the dataframe, it will be created
    :param city: The city of interest. This is important because traffic data will be created synthetically via
    route simulations in the city.
    :param k_drive, k_bike, k_walk: The number of routes to be simulated with driving, going by bike and walking
    """
    def __init__(self, data: gpd.GeoDataFrame, city: str, k_drive: int, k_bike: int, k_walk: int):
        print("Traffic Dataframe class has been loaded.")
        # Initialize all elements and call functions one after the other
        self.data, self.city, self.k_drive, self.k_bike, self.k_walk = data, city, k_drive, k_bike, k_walk
        self.node_coordinates_drive, self.node_coordinates_bike, self.node_coordinates_walk = self.route_instances()
        # The method route_instances() uses the function create_routes(). The method merge_data() is executed in the
        # main file to return the dataframe directly in the main file and not a TrafficDataframe object in order to
        # pipeline the dataframe to the next class.

    def create_routes(self, network_type: str, k: int):
        """
        This function takes a network type and an integer and creates as much routes throughout the network
        :param network_type: The network type, i.e., "drive", "bike" or "walk"
        :param k: The number of routes to be simulated
        :return: A very long list with the shapely.geometry Point of each node and each edge on the path of each single
        simulated route. Additionally, the Point of each node in each of the three networks is added for Laplacian
        smoothing
        """
        # Create a graph of the desired network type and randomly pick k start and end nodes in this graph
        graph = ox.graph_from_place(self.city, network_type=network_type)
        start_nodes = random.choices(list(graph.nodes()), k=k)
        end_nodes = random.choices(list(graph.nodes()), k=k)
        # Nodes is a list of lists of which each list corresponds to one route by the shortest path
        # One route consists of a list of nodes that are passed by the route
        nodes = []
        for i in range(k):
            try:
                nodes.append(nx.shortest_path(graph, start_nodes[i], end_nodes[i], weight="length"))
            # NetworkXNoPath can happen if a route goes through one-way streets or other weird things happen
            # This error is experienced to happen in less than 1 percent of the routes to be simulated. These routes
            # which we tried to simulated are then just overleaped
            except nx.NetworkXNoPath:
                continue
        # Node coordinates is a list with the coordinates of all edges on each route. This initializes the final list
        # which is returned in the end
        node_coordinates = []
        # Take each single route
        for route in nodes:
            # Iterate over the number of edges on this route
            for i in range(len(ox.utils_graph.get_route_edge_attributes(graph, route))):
                # Take each edge on the route and the coords of its geometry attribute and write is shapely.geometry
                # Point to the list
                try:
                    for element in ox.utils_graph.get_route_edge_attributes(graph, route)[i]["geometry"].coords:
                        node_coordinates.append(Point(element))
                # For some reasons, not each edge on the route has got a geometry attribute, so these edges are just
                # overleaped
                except KeyError:
                    continue
        # Nodes disentangles the list of lists structure
        nodes = [node for route in nodes for node in route]
        # Generally, for each node in the graph, the coordinate gets written to the final coordinates
        for node, data in graph.nodes(data=True):
            node_coordinates.append(Point((data["x"], data["y"])))
        # For each node on each route, the coordinate gets written to the final coordinates
        for element in nodes:
            node_coordinates.append([Point((data["x"], data["y"])) for node, data in graph.nodes(data=True)
                                     if node == element][0])
        return node_coordinates

    def route_instances(self):
        # Finally create the routes. Apply the k_drive, k_bike, k_walk parameters to the create_routes() function
        # and return the node coordinates as a tuple
        self.node_coordinates_drive = self.create_routes(network_type="drive", k=self.k_drive)
        self.node_coordinates_bike = self.create_routes(network_type="bike", k=self.k_bike)
        self.node_coordinates_walk = self.create_routes(network_type="walk", k=self.k_walk)
        return self.node_coordinates_drive, self.node_coordinates_bike, self.node_coordinates_walk

    def merge_data(self):
        # Initialize and increment traffic attribute. If there is already a traffic attribute in the dataframe, it will
        # be set back to 0. For each single Point in the node_coordinates list, the cell in which to Point lies gets
        # incremented by one. The dataframe then is returned back
        self.data["traffic"] = 0
        for element in self.node_coordinates_drive:
            self.data.loc[element.within(self.data["geometry"]), "traffic"] += 1
        for element in self.node_coordinates_bike:
            self.data.loc[element.within(self.data["geometry"]), "traffic"] += 1
        for element in self.node_coordinates_walk:
            self.data.loc[element.within(self.data["geometry"]), "traffic"] += 1
        return self.data

    def plot_traffic_heatmap(self, data: gpd.GeoDataFrame, cells_lat: int, cells_lon: int):
        """
        This function plots a heatmap of the traffic attribute. The heatmap in the end traces the main traffic roads
        throughout the city
        :param data: The dataframe with the traffic attribute
        :param cells_lat: The number of grid cells in latitude
        :param cells_lon: The number of grid cells in longitude. This is important to know the dimensions of the
        heatmap
        :return: A matplotlib.pyplot plot of the heatmap. This plot is saved as an .html file
        """
        filename = "traffic_heatmap.png"
        # Take only the traffic attribute of the data, take its pure values and reshape the form to display it
        traffic = data["traffic"].values.reshape(cells_lat, cells_lon)
        a = plt.imshow(traffic, cmap="hot", interpolation="nearest")
        plt.savefig(filename)
        webbrowser.open("file://" + os.path.realpath(filename))

    def save_csv(self, data: gpd.GeoDataFrame, name: str):
        data.to_csv(name)