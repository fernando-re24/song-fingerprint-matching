"""
Defines the index for the fingerprints collection, the hash field.
Author: Fernando Rivas Espinoza
"""

from backend.db.connection import fingerprints_collection


def create_indexes():
    fingerprints_collection.create_index("hash")
