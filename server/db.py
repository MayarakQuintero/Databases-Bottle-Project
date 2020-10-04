"""
Wraps a single connection to the database with higher-level functionality.

@author: diego - mayarak
"""

from psycopg2.extras import RealDictCursor
from relations import Inspection, Restaurant, Tweet
from strsimpy.jaro_winkler import JaroWinkler


class DB:
    '''
    Class for handling database connection
    '''


    def __init__(self, connection):
        self.conn = connection

    def clean_restaurants(self):
        '''
        '''
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('select * from ri_restaurants;')
        results = cur.fetchall()
        restaurants = []
        for row in results:            
            if not row['clean']:
                restaurant = Restaurant(row)
                restaurants.append(restaurant)
                restaurant.update_clean(cur)
                
        matches = {}
        matched_restaurants = set()
        for i in range(len(restaurants)):
            if type(matches.get(i)) != list:
                matches[i] = []
            for j in range(i + 1, len(restaurants)):
                similarity = restaurants[i].compare_distance(restaurants[j])
                
                if similarity >= 0.75:
                    if restaurants[j] in matched_restaurants:
                        continue
                    matches[i].append(restaurants[j])
                    matched_restaurants.add(restaurants[j])
        
        matched_restaurants = set()
        for i in sorted(matches):
            if matches[i]:
                for restaurant in matches[i]:
                    if restaurant.data['id'] in matched_restaurants:
                        continue
                    matched_restaurants.add(restaurant.data['id'])
                    self.update_matches_in_database(cur, restaurants[i], restaurant)
        cur.close()
    
    def clean_restaurants_all(self):
        '''
        '''
        cur = self.conn.cursor()
        cur.execute('SELECT id, name, address, zip FROM ri_restaurants WHERE clean = false;')
        results = cur.fetchall()
        restaurants = []
        for row in results:            
            # restaurant = Restaurant(row)
            restaurants.append(row)
            # restaurant.update_clean(cur)

        already_blocked =  set()
        for restaurant in restaurants: 
            if not restaurant[0] in already_blocked:
                # table_name = 'a' + str(restaurant[0])
                cur.execute("CREATE TEMP TABLE IF NOT EXISTS table_%s AS SELECT * FROM ri_restaurants WHERE zip = %s;", [restaurant[0], restaurant[3]])
                cur.execute("CREATE INDEX IF NOT EXISTS address_idx on table_%s (address);", [restaurant[0]])
                cur.execute("SELECT * FROM table_%s;", [restaurant[0]])
                blocks = cur.fetchall()
                for block in blocks:
                    already_blocked.add(block[0])

                reviewed = set()
                dict_best_attributes = {'name': [], 'facility_type':[], 'address':[], 'city': [], 'state':[], 'zip':[], 'location':[]}
                for block1 in blocks: 
                    for block2 in blocks:
                        if block2[0] not in reviewed:
                            similarity = self.get_similarity(block1[1], block2[1], block1[2], block2[2])
                            if similarity >= 0.80 and similarity < 1:
                                dict_best_attributes['name'].extend([block1[1],block2[1]])
                                dict_best_attributes['facility_type'].extend([block1[2],block2[2]])
                                dict_best_attributes['address'].extend([block1[3],block2[3]])
                                dict_best_attributes['city'].extend([block1[4],block2[4]])
                                dict_best_attributes['state'].extend([block1[5],block2[5]])
                                dict_best_attributes['zip'].extend([block1[6],block2[6]])
                                dict_best_attributes['location'].extend([block1[7],block2[7]])
                                reviewed.add(block1[0])
                                reviewed.add(block2[0])
                
                if reviewed:
                    cur.execute("SELECT primary_rest_id FROM ri_linked;")
                    primary_rest_ids = cur.fetchall()
                    primary_rid = [value for value in reviewed if value in primary_rest_ids]
                    name = max(dict_best_attributes['name'], key=len)
                    facility_type = max(dict_best_attributes['facility_type'], key = dict_best_attributes['facility_type'].count)
                    address = max(dict_best_attributes['address'], key = dict_best_attributes['address'].count)
                    city = max(dict_best_attributes['city'], key = dict_best_attributes['city'].count)
                    state = max(dict_best_attributes['state'], key = dict_best_attributes['state'].count)
                    zip_ = max(dict_best_attributes['zip'], key = dict_best_attributes['zip'].count)
                    location = max(dict_best_attributes['location'], key = dict_best_attributes['location'].count)
                    list_attr = [name, facility_type, address, city, state, zip_, location]
                    if not primary_rid:
                        cur.execute("INSERT INTO ri_restaurants (id, name, facility_type, address, city, state, zip, location, clean) VALUES\
                         (DEFAULT, (%s), (%s), (%s), (%s), (%s), (%s), (%s), True);", (list_attr))
                    if primary_rid:
                        cur.execute("DELETE FROM ri_restaurants WHERE id = %s;", (primary_rid[0],))
                        cur.execute("DELETE FROM ri_linked WHERE primary_rest_id = %s;", (primary_rid[0],))
                        cur.execute("INSERT INTO ri_restaurants (id, name, facility_type, address, city, state, zip, location, clean) VALUES\
                         (DEFAULT, (%s), (%s), (%s), (%s), (%s), (%s), (%s), True);", (list_attr))
                    cur.execute("SELECT max(id) FROM ri_restaurants;")
                    primary_recordid = cur.fetchone()
                    for i in reviewed:
                        cur.execute('UPDATE ri_inspections SET restaurant_id = (%s) WHERE restaurant_id = (%s);', (primary_recordid[0], i))
                        cur.execute("INSERT INTO ri_linked (primary_rest_id, original_rest_id) VALUES ((%s), (%s));", (primary_recordid[0], i))

        cur.execute('UPDATE ri_restaurants SET clean = \'True\';')
        cur.close()

    def get_similarity(self, name_1, name_2, address_1, address_2):
        jarowinkler = JaroWinkler()
        similarity_address = jarowinkler.similarity(str.upper(address_1), str.upper(address_2))
        similarity_name = jarowinkler.similarity(str.upper(name_1), str.upper(name_2))
        if similarity_address <= 0.85 or similarity_name <= 0.75:
            similarity = 0
        else:
            similarity = (similarity_name + similarity_address)/2
            
        return similarity

    def get_linked_restaurants(self, id):
        '''
        Gets linked restaurants and adds them to a list to return to the 
        server
        '''
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('select original_rest_id from ri_linked where\
                    primary_rest_id = (%s);', [id])
        results = cur.fetchall()
        linked_restaurants = []
        for row in results:
            cur.execute("select * from ri_restaurants where id = (%s);",
                        [row['original_rest_id']])
            restaurant = Restaurant(cur.fetchone())
            linked_restaurants.append(restaurant.data)
        return linked_restaurants

    def update_matches_in_database(self, cur, restaurant_1, restaurant_2):
        '''
        '''
        id_self = restaurant_1.data['id']
        id_other = restaurant_2.data['id']
        id_min = min(id_self, id_other)
        id_max = max(id_self, id_other)
        cur.execute("update ri_inspections set restaurant_id=(%s) where restaurant_id=(%s);",
                    [id_min, id_max])
        cur.execute("insert into ri_linked values ((%s), (%s));",
                    [id_min, id_max])


    def process_tweet(self, json_data, lst):
        '''
        Processes tweet and adds to database if necessary

        Parameters
        ----------
        json_data : dictionary

        Returns
        -------
        list of matches.

        '''
        matches = set()
        tweets = []
        lat = json_data.get('lat')
        lon = json_data.get('long')
        restaurants_within = []
        restaurants_mentioned = []
        if lat and lon:
            lat = float(lat)
            lon = float(lon)
            restaurants_within = self.restaurants_ids_within_radious(lat, lon)
        if lst:
            restaurants_mentioned = self.restaurants_mentioned_in_tweet(lst)

        for r_id in restaurants_within:
            if r_id in restaurants_mentioned:
                match_type = 'both'
                restaurants_mentioned.remove(r_id)
            else:
                match_type = 'geo'
            tweet = Tweet(json_data.get('key'), r_id, match_type)
            tweets.append(tweet)
            matches.add(r_id)

        for r_id in restaurants_mentioned:
            match_type = 'name'
            tweet = Tweet(json_data.get('key'), r_id, match_type)
            tweets.append(tweet)
            matches.add(r_id)

        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        for tweet in tweets:
            tweet.add_to_database(cur)

        return list(matches)


    def find_tweet_keys_by_inspection_id(self, inspection_id):
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        restaurant_id = self.find_restaurant_id_by_inspection_id(inspection_id)
        cur.execute("select tkey from ri_tweetmatch where restaurant_id = (%s);",
            [restaurant_id])
        tkeys = cur.fetchall()
        result = {"tkeys":[]}
        for row in tkeys:
            result["tkeys"].append(row['tkey'])
        cur.close()
        return result


    def restaurants_ids_within_radious(self, lat, lon):
        '''
        Returns list of restaurants ids within 500 meters according to MS3
        method

        Parameters
        ----------
        lat : TYPE
            DESCRIPTION.
        lon : TYPE
            DESCRIPTION.

        Returns
        -------
        int.

        '''
        lst = []
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        if lat and lon:
            upperlower_bounds = [lon - 0.00225001, lon + 0.00225001,
                                 lat - 0.00302190, lat + 0.00302190]
            cur.execute("SELECT id FROM ri_restaurants WHERE location[0]\
                        BETWEEN %s AND %s AND location[1] \
                BETWEEN %s AND %s;", upperlower_bounds)
            table = cur.fetchall()
            for row in table:
                lst.append(row['id'])
        cur.close()
        return lst

    def restaurants_mentioned_in_tweet(self, lst):
        '''


        Parameters
        ----------
        lst : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        restaurants_in_tweet = []
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        table = []
        query = "SELECT id, name FROM ri_restaurants where lower(name) in ("\
                + '%s,'*len(lst) + "%s);"
        cur.execute(query, lst+[""])
        table = cur.fetchall()
            
        cur.close()
        for row in table:
            restaurants_in_tweet.append(row['id'])
        return restaurants_in_tweet

    def find_restaurant(self, restaurant_id):
        """
        Searches for the restaurant with the given ID. Returns None if the
        restaurant cannot be found in the database.
        """
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM ri_restaurants where id = (%s);",
                    [restaurant_id])
        row = cur.fetchone()
        restaurant = None
        if row:
            restaurant = Restaurant(row, restaurant_id)
        if not restaurant:
            return None
        lst = self.get_inspections(restaurant_id)
        dct = {}
        dct['restaurant'] = restaurant.data
        dct['inspections'] = lst
        format_location_1(dct)
        return dct

    def get_inspections(self, restaurant_id):
        '''
        Retrieves all inspections associated to the restaurant with
        restaurant_id.

        Parameters
        ----------
        restaurant_id : id of restaurant.

        Returns
        -------
        rv: dictionary with response.

        '''
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM ri_inspections where restaurant_id = (%s);",
                    [restaurant_id])
        row = cur.fetchall()
        lst = []
        for dct in row:
            inspection = Inspection(dct, restaurant_id)
            inspection.data['date'] = str(dct.get('inspection_date'))
            lst.append(inspection.data)
        return lst

    def add_inspection_for_restaurant(self, data, restaurant_id):
        """
        Finds or creates the restaurant then inserts the inspection and
        associates it with the restaurant.
        """
        response = 200
        cur = self.conn.cursor(cursor_factory=RealDictCursor)

        if not restaurant_id:
            restaurant = self.create_restaurant_from_inspection(data)
            restaurant_id = restaurant.data['restaurant_id']
            response = 201

        inspection = Inspection(data, restaurant_id)
        inspection_values_list = inspection.get_inspection_values()
        if not inspection.in_database(cur):

            cur.execute("INSERT INTO ri_inspections VALUES (%s, %s, %s, %s, %s\
                        , %s, %s)", inspection_values_list)
        cur.close()
        return inspection, response

    def create_restaurant_from_inspection(self, json_data):
        '''
        Creates a restaurant, inserts it into database, and returns it

        Parameters
        ----------
        json_data : dictionary from jason_data data.

        Returns
        -------
        restaurant: a restaurant object.

        '''
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        restaurant_id = 'ri_restaurants_id_seq'
        restaurant = Restaurant(json_data, restaurant_id)
        cur.execute("INSERT INTO ri_restaurants VALUES (nextval(%s), %s, %s,\
                    %s, %s, %s, %s, %s, %s);",
                    restaurant.get_restaurant_values())
        cur.close()
        restaurant_id = self.find_restaurant_by_name_and_address(
                        json_data.get('name'), json_data.get('address'))
        restaurant.update_id(restaurant_id)

        return restaurant

    def find_restaurant_id_by_inspection_id(self, inspection_id):
        '''
        Returns restaurant id found in database with the given inspection_id

        Parameters
        ----------
        inspection_id : int of inspection_id.

        Returns
        -------
        restaurant_id: int with id for the restaurant.

        '''
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        restaurant_id = None
        try:
            cur.execute("SELECT restaurant_id FROM ri_inspections where id =\
                        (%s);", [inspection_id])

            result = cur.fetchone()
            if result:
                restaurant_id = result['restaurant_id']
            else:
                restaurant_id = None
        except Exception:
            self.conn.rollback()
        cur.close()
        return restaurant_id

    def find_restaurant_by_inspection_id(self, inspection_id):
        '''
        Finds a restaurant with inspection id and returns it along with an
        http response

        Parameters
        ----------
        inspection_id : int with inspection_id of inspection.

        Returns
        -------
        restaurant, resp: a Restaurant object and an int with http response

        '''
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        resp = 200
        cur.execute("SELECT * FROM ri_restaurants inner join ri_inspections\
                     on ri_restaurants.id = ri_inspections.restaurant_id \
                     where ri_inspections.id = (%s);", [inspection_id])

        result = cur.fetchone()

        if result:
            restaurant = Restaurant(result, result['restaurant_id']).data
        else:
            restaurant = None
            resp = 404
        cur.close()
        if restaurant:
            format_location_2(restaurant)
        return restaurant, resp


    def find_restaurant_by_name_and_address(self, name, address):
        '''
        Finds and returns a restaurant id by name and address of restaurant

        Returns
        -------
        restaurant_id

        '''
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id FROM ri_restaurants where address = (%s) and \
                    name = (%s);", [address, name])
        row = cur.fetchone()
        restaurant_id = None
        if row:
            restaurant_id = row['id']

        return restaurant_id

    def count_insp(self):
        '''
        Counts the number of records in the ri_inspections table and returns
        a simple json object
        '''
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        resp = 200
        cur.execute("SELECT COUNT(id) FROM ri_inspections;")
        result = cur.fetchone()

        return result, resp

    def reset_db(self, str_tables):
        '''
        Reset the database by truncating all tables in the database
        '''
        cur = self.conn.cursor()
        cur.execute("DROP INDEX IF EXISTS ri_restaurants_name_idx;")
        cur.execute("DROP INDEX IF EXISTS ri_restaurants_location_idx;")
        try:
            query = "TRUNCATE " + str_tables + " RESTART IDENTITY CASCADE;"
            cur.execute(query)
            resp = 200
        except Exception:
            resp = 400
        finally:
            cur.close()
            self.conn.commit()
        return resp

    def bulk_load(self, opened_file):
        '''
        Loads csv file into database, restaurants relation

        Parameters
        ----------
        opened_file : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        self.create_table()
        table = 'csv_table'
        query = "COPY " + table + " FROM STDIN WITH CSV HEADER DELIMITER AS ','"
        cur.copy_expert(query, opened_file)
        cur.execute("INSERT INTO ri_restaurants (name, facility_type, address,\
                    city, state, zip, location) SELECT name, facility_type,\
            address, city, state, zip, location FROM (SELECT * FROM csv_table\
            WHERE address NOT IN (SELECT address FROM ri_restaurants)) AS\
            tempt1;")
        cur.execute("SELECT * FROM csv_table;")
        insp_id = cur.fetchall()
        for dct in insp_id:
            restaurant_id = self.find_restaurant_by_name_and_address(
                dct['name'], dct['address'])
            inspection = Inspection(dct, restaurant_id)
            lst = inspection.get_inspection_values()
            cur.execute("INSERT INTO ri_inspections VALUES \
                        (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO\
                        NOTHING;", lst)
        cur.execute("DROP TABLE csv_table;")
        self.conn.commit()
        cur.close()

    def create_table(self):
        '''
        Creates new temporal hardcoded relation in database

        Returns
        -------
        None.

        '''
        cur = self.conn.cursor()
        cur.execute("DROP TABLE IF EXISTS csv_table;")
        cur.execute("CREATE TABLE IF NOT EXISTS csv_table (id VARCHAR(16),\
            name VARCHAR(60),\
            aka_name VARCHAR(60),\
            facility_type VARCHAR(50),\
            risk VARCHAR(30),\
            address VARCHAR(60),\
            city VARCHAR(30),\
            state CHAR(2),\
            zip CHAR(5),\
            date DATE,\
            inspection_type VARCHAR(30),\
            results VARCHAR(30),\
            violations TEXT,\
            latitude DOUBLE PRECISION,\
            longitude DOUBLE PRECISION,\
            location POINT);")
        self.conn.commit()
        cur.close()


def format_location_1(dct):
    '''
    Formats the location entry separating latitude and longitude from
    location to comply with task 3 by updating the dictionary

    Parameters
    ----------
    dct : dictionary with response to server.

    Returns
    -------
    None.

    '''
    coma_index = dct['restaurant']['location'].find(',')
    dct['restaurant']['longitude'] = dct['restaurant']['location'][(coma_index
                                                                    + 1):-1]
    dct['restaurant']['latitude'] = dct['restaurant']['location'][1:
                                                                  (coma_index)]
    del dct['restaurant']['location']


def format_location_2(dct):
    '''
    Formats the location entry separating latitude and longitude from
    location to comply with task 4 by updating the dictionary

    Parameters
    ----------
    dct : dictionary with response to server.

    Returns
    -------
    None.

    '''
    coma_index = dct['location'].find(',')
    dct['longitude'] = dct['location'][(coma_index + 1):-1]
    dct['latitude'] = dct['location'][1:(coma_index)]
    del dct['location']
