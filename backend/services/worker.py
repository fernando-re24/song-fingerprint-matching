"""
SQS consumer loop -- the entrypoint process for the `matching-container`
ECS/Fargate task.

Flow per the deployed architecture:
    fingerprintGenerator (Lambda) -> SQS -> [this worker]
        -> songs-db (DynamoDB)
        -> match payload

Message body is JSON:

    {"requestId": "...", "fingerprints": [[hash, offset], ...]}

Messages are deleted only after a successful match, so a crash mid-flight
leaves the message to reappear after the visibility timeout instead of
silently dropping a user's request.

Author: Fernando Rivas Espinoza
"""

import json
import logging
import os

from backend.db.connection import MATCH_QUEUE_URL, get_sqs_client
from backend.services.matcher import Matcher

logger = logging.getLogger(__name__)

# Long polling: fewer empty receives, lower cost than tight-loop polling.
WAIT_TIME_SECONDS = 20
MAX_MESSAGES_PER_POLL = 10
VISIBILITY_TIMEOUT = int(os.getenv("VISIBILITY_TIMEOUT", "60"))


def process_message(body: dict, matcher: Matcher) -> dict:
    """Turn one queue message into a match payload."""
    request_id = body.get("requestId")

    if "fingerprints" not in body:
        raise ValueError("message must contain 'fingerprints'")

    fingerprints = [(int(h), int(o)) for h, o in body["fingerprints"]]

    matches = matcher.match(fingerprints)

    return {
        "requestId": request_id,
        "matched": bool(matches),
        "results": [m.to_dict() for m in matches],
    }


def run() -> None:
    """Poll SQS forever."""
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    if not MATCH_QUEUE_URL:
        raise RuntimeError("MATCH_QUEUE_URL is not set")

    sqs = get_sqs_client()
    matcher = Matcher()

    logger.info("matching-container polling %s", MATCH_QUEUE_URL)

    while True:
        response = sqs.receive_message(
            QueueUrl=MATCH_QUEUE_URL,
            MaxNumberOfMessages=MAX_MESSAGES_PER_POLL,
            WaitTimeSeconds=WAIT_TIME_SECONDS,
            VisibilityTimeout=VISIBILITY_TIMEOUT,
        )

        for message in response.get("Messages", []):
            try:
                result = process_message(json.loads(message["Body"]), matcher)
                logger.info(
                    "request=%s matched=%s results=%d",
                    result["requestId"],
                    result["matched"],
                    len(result["results"]),
                )
                sqs.delete_message(
                    QueueUrl=MATCH_QUEUE_URL,
                    ReceiptHandle=message["ReceiptHandle"],
                )
            except Exception:
                # Left on the queue: redelivered after the visibility
                # timeout, and eventually dead-lettered by the queue policy.
                logger.exception("failed to process message %s", message.get("MessageId"))


if __name__ == "__main__":
    run()
