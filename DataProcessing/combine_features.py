# Imports
from collections import defaultdict
import pandas as pd


class CombineData:
    """
        This class provides functionality to combine data from different sources by mapping coordinates to specific
        place types and updating the data accordingly.
        :param data (pandas.DataFrame): The main DataFrame containing the data to be combined and updated.
        :param df (pandas.DataFrame): A DataFrame containing information about place types and their coordinates.

        Methods:
            map_coordinates(): Maps coordinates to specific place types in the main DataFrame and updates the data
                              accordingly.
            __setitem__(key, value): Set an item in the data DataFrame using bracket notation.
            __getitem__(key): Get an item from the data DataFrame using bracket notation.
        """
    def __init__(self, data: pd.DataFrame, df: pd.DataFrame):
        """
        Initialize the CombineData object with data to be combined and a DataFrame containing place type information.
        :param data (pandas.DataFrame): The main DataFrame containing the data to be combined and updated.
        :param df (pandas.DataFrame): A DataFrame containing information about place types and their coordinates.
        """
        print("Combine Data class has been loaded.")
        self.data, self.df = data, df
        self.map_coordinates()

    def map_coordinates(self):
        """
        Maps coordinates to specific place types in the main DataFrame and updates the data accordingly.
        :return pandas.DataFrame: The main DataFrame with updated data.
        """
        # Create a dictionary of types of places with the corresponding coordinates of the places
        dic = defaultdict(list)
        for _, row in self.df.iterrows():
            key = row['place']
            if key in dic.keys():
                dic[key].append(row['geometry'])
            else:
                dic[key] = [row['geometry']]

        # Iterate through all place types and corresponding coordinates to find the correct grid
        for key in dic:
            self.data[key] = 0
            if key in ['water', 'wood']:
                for coord in dic[key]:
                    if coord.geom_type == 'Point':
                        self.data.loc[coord.within(self.data["geometry"]), key] = 1
                        continue
                    elif coord.geom_type == 'Polygon':
                        try:
                            self.data.loc[coord.intersects(self.data["geometry"]), key] = 1
                        except ValueError:
                            print('Polygon does not work')
                    else:
                        try:
                            self.data.loc[coord.intersects(self.data["geometry"]), key] = 1
                        except ValueError:
                            print('Multipolygon does not work')
            else:
                for coord in dic[key]:
                    if coord.geom_type == 'Point':
                        self.data.loc[coord.within(self.data["geometry"]), key] += 1
                        continue
                    elif coord.geom_type == 'Polygon':
                        try:
                            self.data.loc[coord.intersects(self.data["geometry"]), key] += 1
                        except ValueError:
                            print('Polygon does not work')
                    else:
                        try:
                            self.data.loc[coord.intersects(self.data["geometry"]), key] += 1
                        except ValueError:
                            print('Multipolygon does not work')
        return self.data

    def __setitem__(self, key, value):
        """
        Set an item in the data DataFrame using bracket notation.
        :param key: The key (column name) for which the value should be set.
        :param value: The value to be set for the specified key.
        """
        self.data[key] = value

    def __getitem__(self, key):
        """
        Get an item from the data DataFrame using bracket notation.
        :param key: The key (column name) for which the value should be retrieved.
        :return Any: The value corresponding to the specified key in the data DataFrame.
        """
        return self.data[key]
