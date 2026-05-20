"""
Service for matching hashed fingerprints to known songs
Author: Fernando Rivas Espinoza
"""

import numpy as np
import pymongo

# Imports from cpp engine

__all__ = ["Matcher", "match"]


class Matcher:
    def __init__(self, db: pymongo.Database):
        self.db = db

    def match(self, query_fingerprints: np.ndarray) -> list:
        return
