"""
Read/write helpers for the `songs-db` table.

Indexes are no longer created at runtime -- the table and its `HashIndex`
GSI are provisioned by terraform. What lives here is the small set of
access patterns the matcher and ingestion path actually use.

Author: Fernando Rivas Espinoza
"""

from boto3.dynamodb.conditions import Attr, Key

from backend.db.connection import get_dynamodb_table
from backend.db.index import (
    SONG_METADATA_SK,
    CONTENT_TYPE_SONG,
    song_pk,
)

HASH_INDEX_NAME = "HashIndex"

# DynamoDB caps BatchWriteItem at 25 items per request.
BATCH_WRITE_LIMIT = 25


def put_song(item: dict) -> None:
    """Insert a song metadata item, failing if that song already exists."""
    get_dynamodb_table().put_item(
        Item=item,
        ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
    )


def put_fingerprints(items: list[dict]) -> int:
    """Batch-write fingerprint items. Returns the number written."""
    table = get_dynamodb_table()
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
    return len(items)


def query_by_hash(hash_value: int) -> list[dict]:
    """Return every fingerprint item matching one hash, via the GSI."""
    response = get_dynamodb_table().query(
        IndexName=HASH_INDEX_NAME,
        KeyConditionExpression=Key("hashIndex").eq(str(hash_value)),
    )
    return response.get("Items", [])


def get_song(song_id: str) -> dict | None:
    """Fetch one song's metadata item."""
    response = get_dynamodb_table().get_item(
        Key={"PK": song_pk(song_id), "SK": SONG_METADATA_SK}
    )
    return response.get("Item")


def song_exists(title: str, artist: str) -> bool:
    """Check whether a song with this title/artist was already ingested.

    This is a table scan with a filter, which is fine for the batch
    ingestion path but must not be used on the matching hot path.
    """
    response = get_dynamodb_table().scan(
        FilterExpression=(
            Attr("contentType").eq(CONTENT_TYPE_SONG)
            & Attr("title").eq(title)
            & Attr("artist").eq(artist)
        ),
        ProjectionExpression="PK",
        Limit=1,
    )
    return bool(response.get("Items"))
