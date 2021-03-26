# connection.py, creates connection with mongoDB
# author: 1, Edwin Mursia and 2

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

import os
from dotenv import load_dotenv

load_dotenv()
USER = os.getenv('DATABASE_USER')
PASSWORD = os.getenv('DATABASE_PASSWORD')

class dbClient:
       myclient = pymongo.MongoClient(f"mongodb://{USER}:{PASSWORD}@localhost:27017/?authSource=mongoUserAuth&authMechanism=SCRAM-SHA-256")
       database = myclient["status_database"]
       collection = database["server_statuses"]
       idcollection = database["servers"]

# checking the connection
def db_connect_exists():
    try:
        if dbClient.myclient.get_database("status_database"):
            print("Connection Successful")
            return True
    except:
        print("Please check your connection")
        return False

if __name__ == "__main__":
    db_connect_exists()
