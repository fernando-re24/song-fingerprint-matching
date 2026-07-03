"""
AWS resource clients for the matching container.

Replaces the original local MongoDB connection: the deployed architecture
stores song/fingerprint records in DynamoDB (`songs-db`), reads raw audio
from S3 (`audio-payloads`), and consumes match jobs from SQS.

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
AUDIO_BUCKET = os.getenv("AUDIO_BUCKET", "audio-payloads")
MATCH_QUEUE_URL = os.getenv("MATCH_QUEUE_URL", "")

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


@lru_cache(maxsize=1)
def get_s3_client():
    """Return an S3 client for reading raw audio from `audio-payloads`."""
    return boto3.client("s3", config=_BOTO_CONFIG)


@lru_cache(maxsize=1)
def get_sqs_client():
    """Return an SQS client for consuming fingerprint jobs."""
    return boto3.client("sqs", config=_BOTO_CONFIG)
