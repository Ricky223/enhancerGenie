import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from gridfs import GridFS

# Connection string is auto fetched from docker
uri = os.getenv("CONN_STR")

# Set the Stable API version when creating a new client
client = MongoClient(uri)["EnhancerGenePro"]
fs = GridFS(client)
                          
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)