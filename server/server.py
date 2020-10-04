"""
Server script with bottle

@author: diego - mayarak
"""
from bottle import Bottle, post, get, HTTPResponse, request, response
import argparse
import os
import sys
import psycopg2 as pg
import logging
import string
from db import DB

logging.basicConfig(level=logging.INFO)
app = Bottle()
app.COUNT_LOAD_INSPECTIONS = 0
app.TXNSIZE = 1
app.PREVIOUS_TXNSIZE = 1

'''
@author: diego - mayarak
'''


@app.get("/hello")
def hello():
    '''
    Displays hello world in localhost.../hello

    '''
    return "Hello, World! "


@app.get("/restaurants/<restaurant_id:int>")
def find_restaurant(restaurant_id):
    """
    Returns a restaurant and all of its associated inspections.
    """
    db = DB(app.db_connection)
    restaurant = db.find_restaurant(restaurant_id)
    return restaurant


@app.get("/restaurants/by-inspection/<inspection_id>")
def find_restaurant_by_inspection_id(inspection_id):
    """
    Returns a restaurant associated with a given inspection.
    """
    db = DB(app.db_connection)
    restaurant, response_val = db.find_restaurant_by_inspection_id\
        (inspection_id)
    response.status = response_val
    if restaurant is None:
        raise HTTPResponse(status=response_val)
    return restaurant


@app.post("/inspections")
def load_inspection():
    """
    Loads a new inspection (and possibly a new restaurant) into the database.
    """
    app.COUNT_LOAD_INSPECTIONS += 1
    db = DB(app.db_connection)
    json_data = request.json

    restaurant_id = db.find_restaurant_id_by_inspection_id(
        json_data.get('inspection_id'))
    if not restaurant_id:
        name = json_data.get('name')
        address = json_data.get('address')
        restaurant_id = db.find_restaurant_by_name_and_address(name, address)
    inspection, response.status = db.add_inspection_for_restaurant(
        json_data, restaurant_id)

    if app.COUNT_LOAD_INSPECTIONS % app.TXNSIZE == 0:
        db.conn.commit()
        app.COUNT_LOAD_INSPECTIONS = 0

    if inspection:
        return {'restaurant_id': inspection.data.get('restaurant_id')}
    return None
    

@app.get("/txn/<txnsize:int>")
def set_transaction_size(txnsize):
    '''
    Sets the transaction size, which is an attribute of our server bottle

    Parameters
    ----------
    txnsize : int.

    Returns
    -------
    str with log info.

    '''
    app.PREVIOUS_TXNSIZE = app.TXNSIZE
    app.TXNSIZE = txnsize
    db = DB(app.db_connection)
    db.conn.commit()
    return "txnsize changed to: " + str(txnsize)


@app.get("/abort")
def abort_txn():
    '''
    Aborts the current transactions in line, sets counter in bottle to 0
    Returns
    -------
    str
        DESCRIPTION.

    '''

    logging.info("Aborting active transactions")
    db = DB(app.db_connection)
    try:
        app.COUNT_LOAD_INSPECTIONS = 0
        db.conn.rollback()
        return "Active transactions aborted"
    except Exception:
        raise HTTPResponse(status=404)


@app.get("/bulkload/<file_name:path>")
def bulk_load(file_name):
    '''
    Loads file with csv data

    Parameters
    ----------
    file_name : str with filename.

    Raises
    ------
    HTTPResponse
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    base_dir = "../data"
    file_path = os.path.join(base_dir, file_name)
    db = DB(app.db_connection)
    
    try:
        opened_file = open(file_path, "r")
        db.bulk_load(opened_file)

    except Exception:
        raise HTTPResponse(status=404)


@app.get("/reset")
def reset_db():
    '''
    Resets relations in database

    Returns
    -------
    None.

    '''
    logging.info("Reseting DB")
    abort_txn()
    db = DB(app.db_connection)
    response.status = db.reset_db('ri_restaurants, ri_inspections,\
                                  ri_tweetmatch, ri_linked')


@app.get("/count")
def count_insp():
    '''
    Counts the inspections in ri_inspections relation

    Returns
    -------
    count_ins : TYPE
        DESCRIPTION.

    '''
    logging.info("Counting Inspections")
    db = DB(app.db_connection)
    count_ins, response.status = db.count_insp()

    return count_ins


def ngrams(tweet, n_of_words):
    single_word = tweet.translate(str.maketrans('', '', ".")).split()
    output = []
    for i in range(len(single_word)-n_of_words+1):
        output.append(' '.join(single_word[i:i+n_of_words]))
    return output


@app.post("/tweet")
def tweet():
    logging.info("Checking Tweet")
    db = DB(app.db_connection)
    json_data = request.json
    tweet_text = json_data.get('text').lower()
    lst = []
    for i in range(5):
        n_grams_lst = ngrams(tweet_text, i + 1)
        lst += n_grams_lst
    matches = db.process_tweet(json_data, lst)
    db.conn.commit()
    return {'matches': matches}

@app.get("/buildidx")
def build_indexes():
    logging.info("Building indexes")
    db = DB(app.db_connection)
    cur = db.conn.cursor()
    cur.execute("CREATE INDEX ri_restaurants_name_idx on ri_restaurants (name);")
    cur.execute("CREATE INDEX ri_restaurants_location_idx ON ri_restaurants USING GIST (location);")
    cur.close()
    db.conn.commit()


@app.get("/tweets/<inspection_id>")
def find_tweet_keys_by_inspection_id(inspection_id):
    logging.info("Finding tweet keys by inspection ID")
    if not inspection_id:
        return None
    db = DB(app.db_connection)
    tkeys = db.find_tweet_keys_by_inspection_id(inspection_id)
    return tkeys

@app.get("/clean")
def build_indexes():
    logging.info("Cleaning Restaurants")
    db = DB(app.db_connection)
    if app.scaling == True:
        db.clean_restaurants_all()
    if app.scaling == False:
        db.clean_restaurants()

    db.conn.commit()

    
@app.get("/restaurants/all-by-inspection/<inspection_id>")
def find_all_restaurants_by_inspection_id(inspection_id):
    '''
    '''
    logging.info("Get All Restaurants")
    db = DB(app.db_connection)
    restaurant, response_val = db.find_restaurant_by_inspection_id\
        (inspection_id)

    response.status = response_val
    if restaurant is None:
        raise HTTPResponse(status=response_val)
    
    linked_restaurants = db.get_linked_restaurants(restaurant['id'])

    return {'primary': restaurant, 'linked': linked_restaurants}
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config",
        help="The path to the .conf configuration file.",
        default="server.conf"
    )
    parser.add_argument(
        "--host",
        help="Server hostname (default localhost)",
        default="localhost"
    )
    parser.add_argument(
        "-p", "--port",
        help="Server port (default 30235)",
        default=30235,
        type=int
    )

    parser.add_argument(
        "-s","--scaling",
        help="Enable large scale cleaning",
        default=False,
        action="store_true"
    )


    args = parser.parse_args()
    if not os.path.isfile(args.config):
        logging.error("The file \"{}\" does not exist!".format(args.config))
        sys.exit(1)

    app.config.load_config(args.config)
    app.scaling=False
    try:
        app.db_connection = pg.connect(
            dbname=app.config['db.dbname'],
            user=app.config['db.user'],
            password=app.config.get('db.password'),
            host=app.config['db.host'],
            port=app.config['db.port']
        )
    except KeyError as e:
        logging.error("Is your configuration file ({})".format(args.config) +
                      " missing options?")
        raise


    try:
        if args.scaling:
            app.scaling = True
        logging.info("Starting Inspection Service. App Scaling= %s" % (app.scaling))
        app.run(host=args.host, port=args.port)
    finally:
        app.db_connection.close()

