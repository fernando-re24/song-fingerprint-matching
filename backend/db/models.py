"""
Read/write helpers for the `songs-db` table.

Indexes are no longer created at runtime -- the table and its `HashIndex`
GSI are provisioned by terraform. What lives here is the small set of
access patterns the matcher and ingestion path actually use.

Author: Fernando Rivas Espinoza
"""

from backend.db.connection import get_dynamodb_table

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
