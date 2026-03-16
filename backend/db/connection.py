"""
Database connection module for the local MongoDB instance.
Author: Fernando Rivas Espinozas
"""

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")

db = client["song_identifier"]

songs_collection = db["songs"]
fingerprints_collection = db["fingerprints"]
