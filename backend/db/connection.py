"""
Database connection module for the local MongoDB instance.
Author: Fernando Rivas Espinozas
"""

import os

from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

db = client["song_identifier"]

songs_collection = db["songs"]
fingerprints_collection = db["fingerprints"]
