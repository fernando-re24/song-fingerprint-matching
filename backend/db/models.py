"""
Defines the index for the fingerprints collection, the hash field.
Author: Fernando Rivas Espinoza
"""

from backend.db.connection import fingerprints_collection, songs_collection


def create_indexes():
    """Create indexes for efficient fingerprint lookups and duplicate prevention."""
    fingerprints_collection.create_index("hash")
    songs_collection.create_index(
        [("title", 1), ("artist", 1)],
        unique=True,
    )
