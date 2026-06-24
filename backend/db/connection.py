"""
AWS resource clients for the matching container.

Replaces the original local MongoDB connection: the deployed architecture
stores song/fingerprint records in DynamoDB (`songs-db`).

The `popular-songs` Redis cache in the target architecture is not wired up
yet; its client factory belongs here when it is.

Clients are created lazily and cached so a Fargate task opens one
connection pool per process rather than one per SQS message.

Author: Fernando Rivas Espinoza
"""

import os
from functools import lru_cache

import boto3
from botocore.config import Config

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

SONGS_TABLE_NAME = os.getenv("SONGS_TABLE_NAME", "songs-db")

# Retries matter here: Fargate tasks are long-lived and a transient
# throttle should not kill an in-flight match.
_BOTO_CONFIG = Config(
    region_name=AWS_REGION,
    retries={"max_attempts": 5, "mode": "adaptive"},
)


@lru_cache(maxsize=1)
def get_dynamodb_table():
    """Return the `songs-db` DynamoDB table resource."""
    resource = boto3.resource("dynamodb", config=_BOTO_CONFIG)
    return resource.Table(SONGS_TABLE_NAME)
