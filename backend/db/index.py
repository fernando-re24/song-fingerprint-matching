"""
Item builders for the `songs-db` single-table DynamoDB design.

Key schema (see terraform/database.tf):
    PK          partition key
    SK          sort key
    hashIndex   GSI ("HashIndex") partition key, fingerprint lookups
    contentType discriminator: "song" | "fingerprint"

Layout:
    Song         PK="SONG#<song_id>"  SK="METADATA"
    Fingerprint  PK="SONG#<song_id>"  SK="FP#<hash>#<offset>"  hashIndex="<hash>"

Co-locating a song's fingerprints under the same partition key keeps
per-song writes and deletes to a single partition, while the GSI serves the
hash -> songs lookup the matcher needs.

Author: Fernando Rivas Espinoza
"""

SONG_PK_PREFIX = "SONG#"
SONG_METADATA_SK = "METADATA"
FINGERPRINT_SK_PREFIX = "FP#"

CONTENT_TYPE_SONG = "song"
CONTENT_TYPE_FINGERPRINT = "fingerprint"


def song_pk(song_id: str) -> str:
    """Partition key for every item belonging to one song."""
    return f"{SONG_PK_PREFIX}{song_id}"


def create_song(song_id: str, title: str, artist: str, filename: str) -> dict:
    """Build the metadata item for a song."""
    return {
        "PK": song_pk(song_id),
        "SK": SONG_METADATA_SK,
        "contentType": CONTENT_TYPE_SONG,
        "songId": song_id,
        "title": title,
        "artist": artist,
        "filename": filename,
    }


def create_fingerprint(hash_value: int, song_id: str, offset: int) -> dict:
    """Build a single fingerprint item.

    `hashIndex` is stored as a string because DynamoDB GSI keys are typed,
    and the table declares it as S in terraform.
    """
    return {
        "PK": song_pk(song_id),
        "SK": f"{FINGERPRINT_SK_PREFIX}{hash_value}#{offset}",
        "contentType": CONTENT_TYPE_FINGERPRINT,
        "hashIndex": str(hash_value),
        "songId": song_id,
        "offset": offset,
    }
