"""
Defines the documen schema for songs and fingerprints.
Author: Fernando Rivas Espinoza
"""


def create_song(title, artist, filename):
    return {"title": title, "artist": artist, "filename": filename}


def create_fingerprint(hash_value, song_id, offset):
    return {"hash": hash_value, "song_id": song_id, "offset": offset}
