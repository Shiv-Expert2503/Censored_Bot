import pymongo
from logger import logging


def set_up_connection():
    """
    This function setup connection to the database
    """
    uri = MONGODB_URI
    db_name = DMNAME

    client = pymongo.MongoClient(uri)
    database = client[db_name]
    collection_name = COLLECTIONNAME

    try:
        client.admin.command('ping')
        logging.info("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        logging.info("Error Occurred while setting the connection")

    return database, collection_name
