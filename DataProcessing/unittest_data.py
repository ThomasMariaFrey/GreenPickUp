"""
This class contains unit tests for all functions used at any time in the main file to create the dataframe.
"""

import unittest
import pandas as pd
import geopandas as gpd
import os
from shapely.geometry import Polygon, Point
from data_initialization import Dataframe
from data_population import PopulationDataframe
from data_traffic import TrafficDataframe


class TestDataInitialization(unittest.TestCase):
    def test_initialize(self):  # Test the initialize() method
        city, cells_lat, cells_lon = "Stuttgart, Germany", 194, 203
        data_init = Dataframe(city, cells_lat, cells_lon)
        data = data_init.initialize()
        # Test the correct outcomes
        self.assertTrue(isinstance(data, gpd.GeoDataFrame))
        self.assertEqual(len(data), cells_lat * cells_lon)
        self.assertTrue(isinstance(data.geometry.iloc[0], Polygon))
        self.assertTrue("cell_id" in data.columns)
        self.assertTrue("geometry" in data.columns)
        self.assertEqual(len(data.columns), 2)

    def test_display_folium_map(self):  # Test the display_folium_map() method
        city, cells_lat, cells_lon = "Stuttgart, Germany", 194, 203
        data_init = Dataframe(city, cells_lat, cells_lon)
        data = data_init.initialize()
        data_init.display_folium_map(data)
        # This is a basic test to check if the map is displayed without errors. Manually verify the map visually.

    def test_save_csv(self):  # Test the save_csv() method
        city, cells_lat, cells_lon = "Stuttgart, Germany", 194, 203
        data_init = Dataframe(city, cells_lat, cells_lon)
        data = data_init.initialize()
        test_filename = "data_initialization_test.csv"
        data_init.save_csv(data, test_filename)
        read_df = pd.read_csv(test_filename)  # Read back the saved csv file and check its content
        self.assertEqual(len(read_df), cells_lat * cells_lon)
        self.assertTrue("geometry" in read_df.columns)
        self.assertTrue("cell_id" in read_df.columns)
        os.remove(test_filename)  # Clean up the test file


class TestPopulationDataframe(unittest.TestCase):
    def setUp(self):
        # Get the actual data for testing
        data = Dataframe("Stuttgart, Germany", 194, 203).initialize()
        population_data = pd.read_excel("census data Stuttgart.XLSX", sheet_name="Dez", usecols="A:C",
                                        names=["Borough", "District", "Population"])
        self.data_pop = PopulationDataframe(data, population_data)
        self.data = self.data_pop.join_population()

    def test_join_population(self):  # Test the join_population() method
        # Testing only the join_population() method is sufficient because it depends on all previous methods
        self.assertTrue(isinstance(self.data, gpd.GeoDataFrame))
        self.assertTrue(isinstance(self.data.geometry.iloc[0], Polygon))
        self.assertTrue(isinstance(self.data.centroid.iloc[0], Point))
        self.assertTrue("geometry" in self.data.columns)
        self.assertTrue("centroid" in self.data.columns)
        self.assertTrue("population" in self.data.columns)
        self.assertTrue("district" in self.data.columns)

    def test_save_csv(self):  # Test the save_csv() method
        test_filename = "data_population_test.csv"
        self.data_pop.save_csv(self.data, test_filename)
        read_df = pd.read_csv(test_filename)  # Read back the saved csv file and check its content
        self.assertEqual(len(read_df), len(self.data))
        self.assertTrue("geometry" in read_df.columns)
        self.assertTrue("centroid" in read_df.columns)
        self.assertTrue("population" in read_df.columns)
        self.assertTrue("district" in read_df.columns)
        os.remove(test_filename)  # Clean up the test file


class TestTrafficDataframe(unittest.TestCase):
    def setUp(self):
        # Get the actual data for testing
        data = Dataframe("Stuttgart, Germany", 194, 203).initialize()
        self.data_traffic = TrafficDataframe(data, "Stuttgart, Germany", 5, 5, 5)
        self.data = self.data_traffic.merge_data()

    def test_create_routes(self):  # Test the create_routes() method
        drive_coords = self.data_traffic.create_routes(network_type="drive", k=5)
        bike_coords = self.data_traffic.create_routes(network_type="bike", k=5)
        walk_coords = self.data_traffic.create_routes(network_type="walk", k=5)
        self.assertTrue(isinstance(drive_coords, list))
        self.assertTrue(isinstance(bike_coords, list))
        self.assertTrue(isinstance(walk_coords, list))
        self.assertTrue(isinstance(drive_coords[0], Point))
        self.assertTrue(isinstance(bike_coords[0], Point))
        self.assertTrue(isinstance(walk_coords[0], Point))
        # We did not write a unit test for the route_instances() method because we regarded it neglectable.
        # The route_instances() method applies the create_routes() method for the customized specification which we
        # already passed in the unit test for the create_routes() method. There is no use of extra testing the
        # route_instances() method.

    def test_merge_data(self):  # Test the merge_data() method
        self.assertTrue(isinstance(self.data, gpd.GeoDataFrame))
        self.assertTrue("traffic" in self.data.columns)

    def test_plot_traffic_heatmap(self):  # Test the plot_traffic_heatmap() method
        self.data_traffic.plot_traffic_heatmap(self.data, 194, 203)
        # This is a basic test to check if the map is displayed without errors. Manually verify the map visually.

    def test_save_csv(self):  # Test the save_csv() method
        test_filename = "test_traffic_data.csv"
        self.data_traffic.save_csv(self.data, test_filename)
        read_df = pd.read_csv(test_filename)  # Read back the csv file and check its content
        self.assertEqual(len(read_df), len(self.data))
        self.assertTrue("traffic" in read_df.columns)
        os.remove(test_filename)


if __name__ == '__main__':
    unittest.main()
