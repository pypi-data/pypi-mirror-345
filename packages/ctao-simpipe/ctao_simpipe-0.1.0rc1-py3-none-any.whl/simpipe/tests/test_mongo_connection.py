import os

import pymongo


def test_mongo_connection():
    server = os.environ["SIMTOOLS_DB_SERVER"]
    database = os.environ["SIMTOOLS_DB_SIMULATION_MODEL"]
    user = os.environ["SIMTOOLS_DB_API_USER"]
    password = os.environ["SIMTOOLS_DB_API_PW"]
    port = int(os.environ["SIMTOOLS_DB_API_PORT"])

    url = f"mongodb://{user}:{password}@{server}:{port}/{database}"
    client = pymongo.MongoClient(url)
    db = client[database]
    # will fail in case of wrong auth:
    db.list_collection_names()
