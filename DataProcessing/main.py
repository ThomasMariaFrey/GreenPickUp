# Imports
from data_initialization import Dataframe
from data_population import PopulationDataframe
from get_places import OSMPlaces
# from get_map import MapPlaces
from combine_features import CombineData
from data_traffic import TrafficDataframe
import osmnx as ox
import pandas as pd


class Main:
    """
    This class orchestrates the data processing and feature combination workflow to generate a final dataset for
    Reinforcement Learning-based applications.It performs data initialization, population data integration,
    traffic data simulation, OpenStreetMap (OSM) places extraction, combining the extracted places with the data,
    and exporting the final dataset.
    The class is primarily designed to be run as the main entry point of the script.

    Methods:
        run(): Executes the entire data processing and feature combination workflow.
    """
    def __init__(self, k_drive=5, k_bike=5, k_walk=5):
        """
        Initialize the Main object and set parameters for data processing and feature combination.
        """
        # self.city = input("Please enter the city of interest: ")
        self.city = 'Stuttgart, Germany'
        # Get the centroid of the city and return it as [lat, lon] coordinate
        self.coord = ox.geocode_to_gdf(self.city).to_crs(epsg=3857).centroid.to_crs(epsg=4326).iloc[0]
        self.coord = [self.coord.y, self.coord.x]
        # self.cells_lat = int(input("Please enter the number of latitude grid cells: "))
        # self.cells_lon = int(input("Please enter the number of longitude grid cells: "))
        self.cells_lat, self.cells_lon = 194, 203

        # Define the number of simulated routes for traffic data simulation
        self.k_drive = k_drive
        self.k_bike = k_bike
        self.k_walk = k_walk
        # self.k_drive, self.k_bike, self.k_walk = 5, 5, 5

    def run(self, target_csv='data_rl.csv'):
        """
        Executes the entire data processing and feature combination workflow, including data initialization,
        population data integration, traffic data simulation, OSM places extraction, combining places with data,
        and exporting the final dataset.
        """

        """
        1. Dataframe initialization
        """
        data_init = Dataframe(self.city, self.cells_lat, self.cells_lon)
        data = data_init.initialize()
        # print(data.head())
        # OPTIONAL: Display the grid and save the data as a .csv file
        # data_init.display_folium_map(data)
        # data_init.save_csv(data, 'data_init.csv')

        """
        2. Population Data
        """
        import os

        # Get the current directory of this script
        current_dir = os.path.dirname(os.path.realpath(__file__))

        # Construct the path to the CSV file relative to this script's location
        csv_path = os.path.join(current_dir, "census_data_Stuttgart.XLSX")

        data_population = pd.read_excel(csv_path, sheet_name="Dez", usecols="A:C",
                                        names=["Borough", "District", "Population"])
        # print(data_population.head())
        data_pop = PopulationDataframe(data, data_population)
        data = data_pop.join_population()
        # print(data[data['population'] != 0].head())
        # OPTIONAL: Save the data as a .csv file
        # data_pop.save_csv(data, 'data_pop.csv')

        """
        3. Traffic Data
        """
        data_traffic = TrafficDataframe(data, self.city, self.k_drive, self.k_bike, self.k_walk)
        data = data_traffic.merge_data()
        # print(data[data['traffic'] != 0].head())
        # OPTIONAL: Display a heatmap of the traffic attribute and save the data as a .csv file
        # data_traffic.plot_traffic_heatmap(data, self.cells_lat, self.cells_lon)
        # data_traffic.save_csv(data, 'data_traffic.csv')

        """
        4. OSM Places Extraction
        """
        # Mine the places from the OpenStreetMap API
        places = OSMPlaces(self.city)
        df_places = places.get_osm_places()
        # OPTIONAL: Explore and Visualise some place types
        # m = MapPlaces(df_places, self.coord)
        # m.show_map(filename="routes.html")
        # OPTIONAL: Export the dataset for the Front End
        # df_places.to_csv('df_frontend.csv', index=False)

        """
        5. Combine the places extraction with the dataframe
        """
        comb_places = CombineData(data, df_places)
        data = comb_places.map_coordinates()
        # print(data.head())

        """
        6. Export final dataset
        """
        # Export the final dataset for the Reinforcement Learning
        data.to_csv("RL/"+target_csv, index=False)
        print('Successfully executed.')
        return 'Successfully generated the data set.'


if __name__ == "__main__":
    main = Main()
    main.run()
