# -*- coding: utf-8 -*-
"""
Created on Mon May 18 18:27:36 2020

@author: diego - mayarak
"""
from strsimpy.jaro_winkler import JaroWinkler


INSPECTION_ID = 'inspection_id'
STATE = 'state'
NAME = 'name'
RISK = 'risk'
ADDRESS = 'address'
INSPECTION_DATE = 'date'
INSPECTION_TYPE = 'inspection_type'
VIOLATIONS = 'violations'
RESULTS = 'results'
FACILITY_TYPE = 'facility_type'
CITY = 'city'
ZIP = 'zip'
LOCATION = 'location'
RESTAURANT_ID = 'restaurant_id'
CLEAN = 'clean'
ID = 'id'
TKEY = 'tkey'
MATCH = 'match'


class Tweet:
    '''
    Inspection class to represent inspection data
    '''

    def __init__(self, tkey, restaurant_id, match):
        '''
        Constructor for Inspection objects

        Parameters
        ----------
        json_data : Data with dictionary given to server
        restaurant_id : Id of restaurant

        '''
        data = {}
        data[TKEY] = tkey
        data[RESTAURANT_ID] = restaurant_id
        data[MATCH] = match
        self.data = data
        self.lst = self.make_list()

    def make_list(self):
        '''
        Makes an ordered list with the inspection data

        Returns
        -------
        lst: list with ordered attributes as the schema of table ri_inspections

        '''
        lst = []
        lst.append(self.data.get(TKEY))
        lst.append(self.data.get(RESTAURANT_ID))
        lst.append(self.data.get(MATCH))
        return lst

    def get_values(self):
        '''
        Returns the list with values ordered as the table schema

        Returns
        -------
        self.lst: list with attributes.

        '''
        return self.lst

    def in_database(self, cur):
        '''
        Checks if self is in database

        Parameters
        ----------
        cur : cursor to query the database to check if self is in it.

        Returns
        -------
        boolean.

        '''
        cur.execute("SELECT count(tkey) FROM ri_tweetmatch where tkey =\
                    (%s);", [self.data.get(TKEY)])
        result = cur.fetchone()
        return result.get('count') == 1

    def add_to_database(self, cur):
        '''
        Adds tweet to database

        Parameters
        ----------
        cur : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        cur.execute("insert into ri_tweetmatch values (%s, %s, %s)\
                    on conflict (tkey, restaurant_id) do nothing;;",
                    self.lst)


class Inspection:
    '''
    Inspection class to represent inspection data
    '''

    def __init__(self, json_data, restaurant_id):
        '''
        Constructor for Inspection objects

        Parameters
        ----------
        json_data : Data with dictionary given to server
        restaurant_id : Id of restaurant

        '''
        data = {}
        inspection_id = json_data.get(INSPECTION_ID, None)
        if not inspection_id:
            inspection_id = json_data.get(ID, None)
        data[ID] = inspection_id
        data[RISK] = json_data.get(RISK, None)
        if data[RISK]:
            data[RISK] = data[RISK][:30]
        data[INSPECTION_DATE] = json_data.get(INSPECTION_DATE, None)
        data[INSPECTION_TYPE] = json_data.get(INSPECTION_TYPE, None)
        if data[INSPECTION_TYPE]:
            data[INSPECTION_TYPE] = data[INSPECTION_TYPE][:30]
        data[RESULTS] = json_data.get(RESULTS, None)
        data[VIOLATIONS] = json_data.get(VIOLATIONS, None)
        data[RESTAURANT_ID] = str(restaurant_id)

        self.data = data
        self.lst = self.make_list()

    def make_list(self):
        '''
        Makes an ordered list with the inspection data

        Returns
        -------
        lst: list with ordered attributes as the schema of table ri_inspections

        '''
        lst = []
        lst.append(self.data.get(ID))
        lst.append(self.data.get(RISK))
        lst.append(self.data.get(INSPECTION_DATE))
        lst.append(self.data.get(INSPECTION_TYPE))
        lst.append(self.data.get(RESULTS))
        lst.append(self.data.get(VIOLATIONS))
        lst.append(self.data.get(RESTAURANT_ID))
        return lst

    def get_inspection_values(self):
        '''
        Returns the list with values ordered as the table schema

        Returns
        -------
        self.lst: list with attributes.

        '''
        return self.lst

    def in_database(self, cur):
        '''
        Checks if self is in database

        Parameters
        ----------
        cur : cursor to query the database to check if self is in it.

        Returns
        -------
        boolean.

        '''
        cur.execute("SELECT count(id) FROM ri_inspections where id =\
                    (%s);", [self.data.get(ID)])
        result = cur.fetchone()
        return result.get('count') == 1


class Restaurant:
    '''
    Restaurant class to represent restaurant data
    '''

    def __init__(self, json_data, restaurant_id=None):
        '''
        Constructor for Restaurant objects

        Parameters
        ----------
        json_data : Data with dictionary given to server
        restaurant_id : Id of restaurant

        '''
        data = {}
        data[NAME] = json_data.get(NAME, None)
        data[FACILITY_TYPE] = json_data.get(FACILITY_TYPE, None)
        data[ADDRESS] = json_data.get(ADDRESS, None)
        data[CITY] = json_data.get(CITY, None)
        data[STATE] = json_data.get(STATE, None)
        data[ZIP] = json_data.get(ZIP, None)
        data[LOCATION] = json_data.get(LOCATION, None)
        if not data[LOCATION]:
            data[LOCATION] = "(0, 0)"
        data[CLEAN] = str(json_data.get(CLEAN, 'False'))
        if restaurant_id:
            data['id'] = str(restaurant_id)
        else:
            data['id'] = json_data.get('id')

        self.data = data
        self.lst = self.make_list()

    def make_list(self):
        '''
        Makes an ordered list with the restaurant data

        Returns
        -------
        lst: list with ordered attributes as the schema of table ri_restaurant.

        '''
        lst = []
        lst.append(self.data.get('id'))
        lst.append(self.data.get(NAME))
        lst.append(self.data.get(FACILITY_TYPE))
        lst.append(self.data.get(ADDRESS))
        lst.append(self.data.get(CITY))
        lst.append(self.data.get(STATE))
        lst.append(self.data.get(ZIP))
        lst.append(self.data.get(LOCATION))
        lst.append(self.data.get(CLEAN))
        return lst

    def get_restaurant_values(self):
        '''
        Returns the list with values ordered as the table schema

        Returns
        -------
        self.lst: list with attributes.

        '''
        return self.lst

    def update_id(self, restaurant_id):
        '''
        Updates id for restaurant since an id was generated in the database.

        Parameters
        ----------
        restaurant_id : id of restaurant

        Returns
        -------
        None.

        '''
        self.data[RESTAURANT_ID] = restaurant_id
        self.lst[0] = restaurant_id

    def in_database(self, cur):
        '''
        Checks if self is in database

        Parameters
        ----------
        cur : cursor to query the database to check if self is in it.

        Returns
        -------
        boolean.

        '''
        cur.execute("SELECT count(id) FROM ri_restaurants where id =\
                    (%s);", [self.data.get(RESTAURANT_ID)])
        result = cur.fetchone()
        return result.get('count') == 1


    def update_clean(self, cur):
        '''
        '''
        self.data['clean'] = True
        cur.execute('update ri_restaurants set clean =\'True\''\
                    + ' where id = ' + str(self.data.get('id')))


    def compare_distance(self, other):
        '''
        '''
        jarowinkler = JaroWinkler()
        dist_1 = jarowinkler.similarity(str.lower(self.data['name']),
                                        str.lower(other.data['name']))
        dist_2 = jarowinkler.similarity(str.lower(self.data['address']),
                                        str.lower(other.data['address']))
        if dist_2 > 0.85:
            return dist_1
        return 0


    def add_to_database(self, cur):
        '''
        '''
        cur.execute("INSERT INTO ri_restaurants VALUES (nextval(%s), %s, %s,\
                    %s, %s, %s, %s, %s, %s);",
                    self.get_restaurant_values())
