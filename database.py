import pymongo
from logger import logging


def set_up_connection():
    """
    This function setup connection to the database
    """
    uri = "mongodb+srv://shivansh1:abcdefghijk@cluster0.yc3hy9y.mongodb.net/?retryWrites=true&w=majority"
    db_name = "coders-magglu-keee"

    client = pymongo.MongoClient(uri)
    database = client[db_name]
    collection_name = "harry-puttar"

    try:
        client.admin.command('ping')
        logging.info("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        logging.info("Error Occurred while setting the connection")

    return database, collection_name
