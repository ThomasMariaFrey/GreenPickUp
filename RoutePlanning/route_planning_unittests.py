"""
This class contains unit tests for the route planning files.
It consists of some edge cases and ensures its correct handling.
"""

import unittest
import pandas as pd
import os
from route_planning import RoutePlanning

# Dataset test1 uses four actions and four time points and optimal routes are visually unambiguous
test1 = pd.DataFrame({"DataSet": ["data_1", "data_2", "data_3", "data_4"],
                      "Action1": ["[48.842455, 9.207929]", "[48.740808, 9.218746]", "[48.723032, 9.092919]",
                                  "[48.817142, 9.108537]"],
                      "Action2": ["[48.822906, 9.110769]", "[48.840421, 9.225954]", "[48.734016, 9.210335]",
                                  "[48.714878, 9.105965]"],
                      "Action3": ["[48.736167, 9.116093]", "[48.825053, 9.096521]", "[48.847990, 9.227499]",
                                  "[48.737865, 9.229904]"],
                      "Action4": ["[48.748279, 9.205185]", "[48.731751, 9.096867]", "[48.817707, 9.088968]",
                                  "[48.833755, 9.199518]"]})

# Dataset test2 adds more actions
test2 = pd.DataFrame({"DataSet": ["data_1", "data_2", "data_3", "data_4"],
                      "Action1": ["[48.842455, 9.207929]", "[48.822906, 9.110769]", "[48.736167, 9.116093]",
                                  "[48.748279, 9.205185]"],
                      "Action2": ["[48.740808, 9.218746]", "[48.840421, 9.225954]", "[48.825053, 9.096521]",
                                  "[48.731751, 9.096867]"],
                      "Action3": ["[48.723032, 9.092919]", "[48.734016, 9.210335]", "[48.847990, 9.227499]",
                                  "[48.817707, 9.088968]"],
                      "Action4": ["[48.817142, 9.108537]", "[48.714878, 9.105965]", "[48.737865, 9.229904]",
                                  "[48.833755, 9.199518]"],
                      "Action5": ["[48.794007, 9.168169]", "[48.764749, 9.185109]", "[48.801442, 9.181279]",
                                  "[48.768239, 9.195180]"],
                      "Action6": ["[48.778333, 9.128833]", "[48.770482, 9.151415]", "[48.782176, 9.153456]",
                                  "[48.762843, 9.151398]"],
                      "Action7": ["[48.803645, 9.213422]", "[48.822953, 9.215356]", "[48.817232, 9.251376]",
                                  "[48.800100, 9.229723]"]})

# Dataset test3 adds an additional place (i.e., time point)
test3 = pd.DataFrame({"DataSet": ["data_1", "data_2", "data_3", "data_4", "data_5"],
                      "Action1": ["[48.842455, 9.207929]", "[48.822906, 9.110769]", "[48.736167, 9.116093]",
                                  "[48.748279, 9.205185]", "[48.813032, 9.116221]"],
                      "Action2": ["[48.740808, 9.218746]", "[48.840421, 9.225954]", "[48.825053, 9.096521]",
                                  "[48.731751, 9.096867]", "[48.852964, 9.152747]"],
                      "Action3": ["[48.723032, 9.092919]", "[48.734016, 9.210335]", "[48.847990, 9.227499]",
                                  "[48.817707, 9.088968]", "[48.746777, 9.234362]"],
                      "Action4": ["[48.817142, 9.108537]", "[48.714878, 9.105965]", "[48.737865, 9.229904]",
                                  "[48.833755, 9.199518]", "[48.737050, 9.126905]"],
                      "Action5": ["[48.794007, 9.163169]", "[48.764749, 9.185109]", "[48.801442, 9.181279]",
                                  "[48.768239, 9.195180]", "[48.784786, 9.170979]"]})

# Dataset test4 has two stations at the same place at a time
test4 = pd.DataFrame({"DataSet": ["data_1", "data_2", "data_3", "data_4", "data_5"],
                      "Action1": ["[48.842455, 9.207929]", "[48.842455, 9.207929]", "[48.736167, 9.116093]",
                                  "[48.748279, 9.205185]", "[48.813032, 9.116221]"],
                      "Action2": ["[48.740808, 9.218746]", "[48.840421, 9.225954]", "[48.825053, 9.096521]",
                                  "[48.731751, 9.096867]", "[48.852964, 9.152747]"],
                      "Action3": ["[48.723032, 9.092919]", "[48.734016, 9.210335]", "[48.847990, 9.227499]",
                                  "[48.817707, 9.088968]", "[48.746777, 9.234362]"],
                      "Action4": ["[48.817142, 9.108537]", "[48.714878, 9.105965]", "[48.737865, 9.229904]",
                                  "[48.833755, 9.199518]", "[48.737050, 9.126905]"],
                      "Action5": ["[48.794007, 9.163169]", "[48.764749, 9.185109]", "[48.801442, 9.181279]",
                                  "[48.768239, 9.195180]", "[48.784786, 9.170979]"]})

# Dataset test5 has a route staying at the same place for two time points
test5 = pd.DataFrame({"DataSet": ["data_1", "data_2", "data_3", "data_4", "data_5"],
                      "Action1": ["[48.842455, 9.207929]", "[48.842455, 9.207929]", "[48.736167, 9.116093]",
                                  "[48.748279, 9.205185]", "[48.813032, 9.116221]"],
                      "Action2": ["[48.740808, 9.218746]", "[48.840421, 9.225954]", "[48.825053, 9.096521]",
                                  "[48.731751, 9.096867]", "[48.852964, 9.152747]"],
                      "Action3": ["[48.723032, 9.092919]", "[48.734016, 9.210335]", "[48.847990, 9.227499]",
                                  "[48.817707, 9.088968]", "[48.746777, 9.234362]"],
                      "Action4": ["[48.817142, 9.108537]", "[48.714878, 9.105965]", "[48.737865, 9.229904]",
                                  "[48.833755, 9.199518]", "[48.737050, 9.126905]"],
                      "Action5": ["[48.794007, 9.163169]", "[48.764749, 9.185109]", "[48.801442, 9.181279]",
                                  "[48.768239, 9.195180]", "[48.784786, 9.170979]"]})


class TestRoutePlanning(unittest.TestCase):
    def test_create_routes(self):
        # Test 1
        route_planner1 = RoutePlanning(city="Stuttgart, Germany", locations=test1)
        routes1 = route_planner1.get_routes()
        self.assertIsNotNone(routes1)
        self.assertIsInstance(routes1, list)

        # Test 2
        route_planner2 = RoutePlanning(city="Stuttgart, Germany", locations=test2)
        routes2 = route_planner2.get_routes()
        self.assertIsNotNone(routes2)
        self.assertIsInstance(routes2, list)

        # Test 3
        route_planner3 = RoutePlanning(city="Stuttgart, Germany", locations=test3)
        routes3 = route_planner3.get_routes()
        self.assertIsNotNone(routes3)
        self.assertIsInstance(routes3, list)

        # Test 4
        route_planner4 = RoutePlanning(city="Stuttgart, Germany", locations=test4)
        routes4 = route_planner4.get_routes()
        self.assertIsNotNone(routes4)
        self.assertIsInstance(routes4, list)

        # Test 5
        route_planner5 = RoutePlanning(city="Stuttgart, Germany", locations=test5)
        routes5 = route_planner5.get_routes()
        self.assertIsNotNone(routes5)
        self.assertIsInstance(routes5, list)

        # Test 6 - Dataset 5, but a depot is added
        route_planner6 = RoutePlanning(city="Stuttgart, Germany", locations=test5, depot=(48.778, 9.155))
        routes6 = route_planner6.get_routes()
        self.assertIsNotNone(routes6)
        self.assertIsInstance(routes6, list)

        # Test 7 - Dataset 5, but a depot is added and the weight is changed to duration
        route_planner7 = RoutePlanning(city="Stuttgart, Germany", locations=test5, depot=(48.778, 9.155),
                                       weight="duration")
        routes7 = route_planner7.get_routes()
        self.assertIsNotNone(routes7)
        self.assertIsInstance(routes7, list)

    def test_plot_routes_osmnx(self):
        # Test 1
        route_planner1 = RoutePlanning(city="Stuttgart, Germany", locations=test1)
        route_planner1.plot_routes_osmnx()  # Manually verify the result

        # Test 2 - Reduced to dataset 5 with depot
        route_planner2 = RoutePlanning(city="Stuttgart, Germany", locations=test5, depot=(48.778, 9.155))
        route_planner2.plot_routes_osmnx()  # Manually verify the result

    def test_plot_routes_folium(self):
        # Test 1
        route_planner1 = RoutePlanning(city="Stuttgart, Germany", locations=test1)
        test_filename = "test_folium_map.html"
        route_planner1.plot_routes_folium(test_filename)  # Manually verify the result
        self.assertTrue(os.path.exists(test_filename))
        os.remove(test_filename)  # Clean up the test file

        # Test 2
        route_planner2 = RoutePlanning(city="Stuttgart, Germany", locations=test2)
        test_filename = "test_folium_map.html"
        route_planner2.plot_routes_folium(test_filename)  # Manually verify the result
        self.assertTrue(os.path.exists(test_filename))
        os.remove(test_filename)  # Clean up the test file

        # Test 3
        route_planner3 = RoutePlanning(city="Stuttgart, Germany", locations=test3)
        test_filename = "test_folium_map.html"
        route_planner3.plot_routes_folium(test_filename)  # Manually verify the result
        self.assertTrue(os.path.exists(test_filename))
        os.remove(test_filename)  # Clean up the test file

        # Test 4
        route_planner4 = RoutePlanning(city="Stuttgart, Germany", locations=test4)
        test_filename = "test_folium_map.html"
        route_planner4.plot_routes_folium(test_filename)  # Manually verify the result
        self.assertTrue(os.path.exists(test_filename))
        os.remove(test_filename)  # Clean up the test file

        # Test 5
        route_planner5 = RoutePlanning(city="Stuttgart, Germany", locations=test5)
        test_filename = "test_folium_map.html"
        route_planner5.plot_routes_folium(test_filename)  # Manually verify the result
        self.assertTrue(os.path.exists(test_filename))
        os.remove(test_filename)  # Clean up the test file

        # Test 6
        route_planner6 = RoutePlanning(city="Stuttgart, Germany", locations=test5, depot=(48.778, 9.155))
        test_filename = "test_folium_map.html"
        route_planner6.plot_routes_folium(test_filename)  # Manually verify the result
        self.assertTrue(os.path.exists(test_filename))
        os.remove(test_filename)  # Clean up the test file

        # Test 7
        route_planner7 = RoutePlanning(city="Stuttgart, Germany", locations=test5, depot=(48.778, 9.155),
                                       weight="duration")
        test_filename = "test_folium_map.html"
        route_planner7.plot_routes_folium(test_filename)  # Manually verify the result
        self.assertTrue(os.path.exists(test_filename))
        os.remove(test_filename)  # Clean up the test file


if __name__ == "__main__":
    unittest.main()
