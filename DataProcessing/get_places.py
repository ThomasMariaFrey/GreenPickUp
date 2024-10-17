# Imports
import pandas as pd
import osmnx as ox


class OSMPlaces:
    """
    This class provides functionality to retrieve and process various types of places from the OpenStreetMap API
    using the OSMnx library and generate a DataFrame containing relevant information about these places.
    :param city (str): The name of the city for which OSM places will be retrieved.

    Methods:
        get_osm_places(): Retrieves various types of OSM places, processes the data, and returns a DataFrame
                         containing information about the selected places.
    """

    def __init__(self, city: str):
        """
        Initialize the OSMPlaces object with the specified city.
        :param city (str): The name of the city for which OSM places will be retrieved.
         """
        print("Dataframe Get OSM Places class has been loaded.")
        # Initialize all elements
        self.city = city

    def get_osm_places(self):
        """
        Retrieves various types of OSM places, processes the data, and returns a DataFrame containing information
        about the selected places.
        All the code blocks in the function follow the same structure: First, tags are defined for the places that
        shall be retrieved from the OSM API as a dictionary. Second, the API request is made. Third, some manipulations
        of column merging and selection are made.
        :return: pandas.DataFrame: A DataFrame containing information about selected OSM places, including columns for
        place type, geometry, name, address, and postcode.
        """
        # First: Amenities
        tags = {'amenity': ['post_office', 'parcel_locker', 'post_depot', 'college', 'university', 'kindergarten',
                            'school', 'library', 'nursing_home', 'hospital', 'pharmacy', 'charging_station', 'parking',
                            'bus_station', 'atm', 'bank', 'arts_center', 'cinema', 'theatre']}
        amenities = ox.geometries_from_place(self.city, tags=tags)
        amenities['address'] = amenities['addr:street'] + ' ' + amenities['addr:housenumber']
        amenities = amenities[['amenity', 'geometry', 'name', 'address', 'addr:postcode']]

        # Second: Landuse
        tags = {'landuse': ['depot', 'residential', 'commercial', 'industrial', 'construction', 'depot']}
        landuse = ox.geometries_from_place(self.city, tags=tags)
        landuse['address'] = landuse['addr:street'] + ' ' + landuse['addr:housenumber']
        landuse = landuse[['landuse', 'geometry', 'name', 'address', 'addr:postcode']]

        # Third: Public Transport
        tags = {'public_transport': 'station'}
        public_transport = ox.geometries_from_place(self.city, tags=tags)
        public_transport['address'] = public_transport['addr:street'] + ' ' + public_transport['addr:housenumber']
        public_transport = public_transport[['public_transport', 'geometry', 'name', 'address', 'addr:postcode']]

        # Fourth: Barriers
        tags = {'barrier': 'cycle_barrier'}
        barrier = ox.geometries_from_place(self.city, tags=tags)
        barrier = barrier[['barrier', 'geometry']]

        # Fifth: Buildings
        tags = {'building': ['house', 'apartments', 'commercial', 'industrial', 'office', 'retail', 'supermarket',
                             'civic', 'public', 'religious', 'sports_hall', 'stadium', 'parking']}
        buildings = ox.geometries_from_place(self.city, tags=tags)
        buildings['address'] = buildings['addr:street'] + ' ' + buildings['addr:housenumber']
        buildings = buildings[['building', 'geometry', 'name', 'address', 'addr:postcode']]

        # Sixth: Nature
        tags = {'natural': ['water', 'wood']}
        nature = ox.geometries_from_place(self.city, tags=tags)
        nature = nature[['natural', 'geometry', 'name']]

        # Concatenate the sixth obtained dataframes together and some manipulations
        places = pd.concat([amenities, landuse, public_transport, barrier, buildings, nature], axis=0,
                           ignore_index=True)
        places = places.drop_duplicates()
        places = places.rename(columns={"addr:postcode": "postcode"})
        places['place'] = places['amenity']
        places['place'] = places['place'].fillna(places['landuse'])
        places['place'] = places['place'].fillna(places['public_transport'])
        places['place'] = places['place'].fillna(places['barrier'])
        places['place'] = places['place'].fillna(places['building'])
        places['place'] = places['place'].fillna(places['natural'])
        # print('Number of places extracted: ', len(places))

        # Create the finale dataframe with places and drop the not needed categories
        tags = ['post_office', 'parcel_locker', 'post_depot', 'college', 'university', 'kindergarten',
                'school', 'library', 'nursing_home', 'hospital', 'pharmacy', 'charging_station', 'parking',
                'bus_station', 'atm', 'bank', 'arts_center', 'cinema', 'theatre', 'depot', 'residential',
                'commercial', 'industrial', 'construction', 'depot', 'station', 'cycle_barrier', 'house', 'apartments',
                'commercial', 'industrial', 'office', 'retail', 'supermarket',
                'civic', 'public', 'religious', 'sports_hall', 'stadium', 'parking', 'water', 'wood']
        df = places[places['place'].isin(tags)].copy()
        df = df[['place', 'geometry', 'name', 'address', 'postcode']]
        df = df.drop_duplicates(subset=['geometry', 'name'], keep='last')
        return df
