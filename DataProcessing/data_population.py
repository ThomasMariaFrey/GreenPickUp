"""
This class takes a dataframe and updates or creates the population attribute
"""
import pandas as pd
import geopandas as gpd
import osmnx as ox


class PopulationDataframe:
    """
    This class takes a dataframe and updates or creates a population attribute
    :param data: The dataframe to be updated with the traffic attribute. If a traffic attribute is not yet persistent
    in the dataframe, it will be created
    :param data_population: A pandas dataframe with population data
    """
    def __init__(self, data: gpd.GeoDataFrame, data_population: pd.DataFrame):
        print("Population Dataframe class has been loaded.")
        # Initialize all elements and call functions one after the other
        self.data, self.data_population = data, data_population
        self.data_calc()
        self.data_population_calc()
        self.districts_population()
        # The method join_population() is executed in the main file to return the dataframe directly in the main file
        # and not a TrafficDataframe object in order to pipeline the dataframe to the next class.

    def data_calc(self):
        # This function takes the dataframe and prepares it for the join with the population dataframe
        # Set the crs attribute, take the geometry column and pass it to the geo dataframe
        self.data = self.data.set_crs("EPSG:3857")
        geometry = self.data["geometry"]
        self.data = gpd.GeoDataFrame(self.data, geometry=geometry, crs="EPSG:3857")
        # Take the centroid of the cell polygon
        self.data["centroid"] = self.data["geometry"].centroid
        # Rename the geometry column because the geometry attribute will then be passed to the centroid. The centroid
        # need to inherit the geometry attribute because it is the crucial ingredient to map the population density
        self.data.rename(columns={"geometry": "cell_polygon"}, inplace=True)
        self.data = self.data.set_geometry("centroid")
        # Return the dataframe back
        return self.data

    def data_population_calc(self):
        # This function takes the population dataframe and cleans it. This code is highly customized on the concrete
        # population dataframe at hand
        # Drop those records with a NA entry at the district column because those are aggregated values
        self.data_population.dropna(subset=["District"], inplace=True)
        # Keep only these records with a 3-digit number in it in the district column because those are the actual
        # districts. Reset the index
        self.data_population = \
            self.data_population.loc[self.data_population["District"].str.contains("^\d{3}")].reset_index()
        # Fill the borough column NA records with the value from above
        self.data_population["Borough"].fillna(method="ffill", inplace=True)
        # Concatenate the districts and the borough column and "Stuttgart". These concatenation yields the best results
        # when passed to the OpenStreetMap API.
        self.data_population["District"] = \
            self.data_population["District"] + " " + self.data_population["Borough"] + " Stuttgart"
        # Drop the columns index and borough
        self.data_population.drop(["index", "Borough"], axis=1, inplace=True)
        # Replace the string "Zuf.-" with "Zuffenhausen" in the districts column for the OSM API
        self.data_population["District"] = \
            self.data_population["District"].str.replace(r"Zuf.-", r"Zuffenhausen-", regex=True)
        # Drop the numbers out of the district designation
        self.data_population["District"] = self.data_population["District"].str.replace("\d+", "", regex=True)
        # Replace the value Hasenberg West Stuttgart with 70197 Hasenberg becasue it creates issues with the OSM API
        self.data_population.loc[self.data_population["District"] == " Hasenberg West Stuttgart", "District"] =\
            "70197 Hasenberg"
        # Return back the population dataframe after all the manipulations
        return self.data_population

    def districts_population(self):
        # This function creates a new population geopandas dataframe with the population data and the OSM polygon for
        # each district
        # Initialize the dictionary that will become the dataframe and take the districts from the population dataframe
        d = {"district": [], "geometry": []}
        districts = self.data_population["District"].tolist()
        # For each district, take the OSM polygon
        for district in range(len(districts)):
            # Oberer Schlossgarten and Hauptbahnhof are exceptions because they need to take the second polygon that is
            # available over the OSM API
            if (districts[district] == " Oberer Schlossgarten Mitte Stuttgart") or \
                    (districts[district] == " Hauptbahnhof Mitte Stuttgart"):
                try:
                    gdf_district = ox.geocoder.geocode_to_gdf(districts[district], which_result=2)
                # It can be from time to time that KeyErrors or ValueErrors arise. We found that it is not predictable
                # which error occurs when and found generally no pattern in the error messages. This just confuses.
                # If such an error occurs, the district is overleaped. That also means that the population density for
                # this district will be set to zero
                except (ValueError, KeyError):
                    continue
            else:
                try:
                    gdf_district = ox.geocoder.geocode_to_gdf(districts[district])
                except (ValueError, KeyError):
                    continue
            d["district"].append(districts[district])
            d["geometry"].append(gdf_district["geometry"][0])
        # Create a new geopandas dataframe with population data and district polygons
        df = pd.DataFrame(d)
        geometry = gpd.GeoSeries.from_wkt(df["geometry"].apply(lambda x: x.wkt), crs="EPSG:3857")
        self.population_gpd = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:3857")
        self.population_gpd["population"] = self.data_population["Population"].tolist()
        # Compute the population density: Take the area of the OSM polygon of the district and normalize it up to the
        # population density per square kilometer. 110602*73493 are the distance in meters for one degree of latitude
        # and longitude, respectively. Normalization by dividing by 1000 is done because a cell is 100x100 meters large
        # and not a square kilometer
        self.population_gpd["population"] = self.population_gpd.apply(
            lambda row: row["population"]/(row["geometry"].area*110602/1000*73493/1000), axis=1).round()
        # Set the geometry attribute for the join and return the population geopandas dataframe
        self.population_gpd.set_geometry("geometry")
        return self.population_gpd

    def join_population(self):
        # This function joins the dataframe with the population dataframe
        # Join the population dataframe to the dataframe based on whether the centroid of the cell polygon lies within
        # the district.
        self.data = gpd.sjoin(self.data, self.population_gpd, how="left", predicate="within")
        # Drop the index of the population dataframe and fill all NA cells with null values. There are NA cells because
        # the grid covers a rectangular and the boundaries of Stuttgart are not a rectangular
        self.data.drop("index_right", axis=1, inplace=True)
        self.data["population"].fillna(0, inplace=True)
        # Rename cell_polygon back to geometry, set its geometry attribute and return back the geopandas dataframe
        self.data.rename(columns={"cell_polygon": "geometry"}, inplace=True)
        self.data.set_geometry("geometry", inplace=True, crs="EPSG:3857")
        return self.data

    def save_csv(self, data: gpd.GeoDataFrame, name: str):
        data.to_csv(name)
