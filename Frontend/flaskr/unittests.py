# Imports
import unittest
from datetime import datetime, date, time
import osmnx as ox

from flaskr.get_helper import Functionalities

class TestFunctionalities(unittest.TestCase):
    """
    This class contains unit tests for the methods defined in the 'Functionalities' class of the 'get_helper' module.
    The tests cover filtering locations by time, finding the nearest node in a graph, calculating the shortest path between nodes,
    and adding map markers with tooltips and icons to a map object.
    Note: To run these tests, make sure the Flask application is properly configured and the necessary packages are installed.
    """

    def setUp(self):
        """
        Set up the test case by initializing an instance of the Functionalities class.
        """
        self.func = Functionalities()

    def test_time_filter(self):
        """
        This test checks whether the time_filter method properly filters locations based on a selected date and time.
        It verifies that the filtered locations list contains the expected values and that the flash message is a string.
        """
        # Define some test timestamps
        locations = [
            {"timestamp_from": datetime(2023, 8, 13, 10, 0, 0)},
            {"timestamp_from": datetime(2023, 8, 13, 12, 0, 0)},
            {"timestamp_from": datetime(2023, 8, 14, 10, 0, 0)}
        ]
        selected_date = date(2023, 8, 13)
        selected_time = time(10, 0, 0)
        filtered_locations, flash_message = self.func.time_filter(locations, selected_date, selected_time)

        # Check that only one location is given back and that it's the correct one
        self.assertEqual(len(filtered_locations), 1)
        self.assertEqual(filtered_locations[0]["timestamp_from"], datetime(2023, 8, 13, 10, 0, 0))

        # Flash message should be a string
        self.assertIsInstance(flash_message, str)

    def test_get_nearest_node(self):
        """
        This test verifies that the get_nearest_node method returns the expected data type (int) for the nearest node ID.
        """
        coords = (48.791664762923176, 9.177939808094296)
        nearest_node = self.func.get_nearest_node(coords)
        # Check that nearest node is of type int
        self.assertIsInstance(nearest_node, int)

    def test_get_shortest_path(self):
        """
        This test checks whether the get_shortest_path method correctly calculates the shortest path between nodes in a graph.
        It ensures that the returned route, route length, and route duration match the expected values.
        """
        graph = ox.graph_from_place("Munich, Germany", network_type="bike", simplify=True)
        source = self.func.get_nearest_node((48.148089, 11.612660))
        target = self.func.get_nearest_node((48.147727, 11.565058))
        route, route_length, route_duration = self.func.get_shortest_path(graph, source, target, 'length')
        # Check whether expected values are received
        self.assertEqual(route, [250932053, 28794004, 27486404, 50754586, 684731, 2246014289, 684734, 10984314785, 
                         1407414185, 10984314792, 10984314796, 1954279, 447528799, 1363439727, 21096414, 1191262009, 
                         1363439758, 1411523375, 1688743346, 1603081266, 1688743345, 1603087104, 4614002762, 2965106712, 
                         1363439503, 3685171862, 1603060326, 1603066225, 601264187, 622114342, 622114339, 616886496, 
                         601266227, 601266925, 3321568273, 2916345912, 1951416996, 118185197, 27039324, 891901175, 
                         112411701, 292679722, 27039342, 129963761, 118237826, 31316069, 270534547, 675082893, 925177412, 
                         1711901468, 27152513, 27152510, 27152490, 372800054, 27270924, 4753785224, 4466373441, 1078841350, 
                         1078841362, 372796999, 7983336, 2889240729, 4030168339, 2589265347, 715327363, 1954365, 2836350886, 
                         2836350889, 433730419, 1315348781, 29565896, 967091764, 618163567, 618163561, 345553442, 7160669063, 
                         21457468, 10142544411, 345553456, 2830356251])
        self.assertEqual(route_length, 4891.1500000000015)
        self.assertEqual(route_duration, 59)

    def test_add_map(self):
        locations = [
            {"latitude": 48.791664762923176, "longitude": 9.177939808094296, "station_id": 1, "timestamp_from": datetime.now().replace(microsecond=0)},
            {"latitude": 48.761895, "longitude": 9.154542, "station_id": 2, "timestamp_from": datetime.now().replace(microsecond=0)},
        ]
        # Marker Configuration
        tooltips = "Station ID: {station_id}, Capacity: {capacity}"
        icon_configs = [{"icon": "circle", "icon_shape": "marker", "background_color": "green"}] * len(locations)
        capacities = {(1, date.today()): 10/20, (2, date.today()): 15/20}
        map_object = self.func.add_map(locations, tooltips, icon_configs, capacities=capacities)

        # Check if map object was created properly        
        self.assertIsNotNone(map_object)

        # Save map as an html file
        map_html_path = "test_map.html"
        map_object.save(map_html_path)

if __name__ == '__main__':
    unittest.main()
