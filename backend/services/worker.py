"""
SQS consumer loop -- the entrypoint process for the `matching-container`
ECS/Fargate task.

Flow per the deployed architecture:
    fingerprintGenerator (Lambda) -> SQS -> [this worker]
        -> songs-db (DynamoDB)
        -> match payload

Message body is JSON. Two shapes are accepted:

    {"requestId": "...", "fingerprints": [[hash, offset], ...]}
        already fingerprinted upstream by the Lambda (normal path)

    {"requestId": "...", "s3Key": "uploads/abc.wav"}
        raw audio still in `audio-payloads`; this worker fingerprints it
        itself using the bundled C++ engine

Messages are deleted only after a successful match, so a crash mid-flight
leaves the message to reappear after the visibility timeout instead of
silently dropping a user's request.

Author: Fernando Rivas Espinoza
"""

import json
import logging
import os
import signal
import tempfile

from backend.db.connection import (
    AUDIO_BUCKET,
    MATCH_QUEUE_URL,
    get_s3_client,
    get_sqs_client,
)
from backend.services.matcher import Matcher

logger = logging.getLogger(__name__)

# Long polling: fewer empty receives, lower cost than tight-loop polling.
WAIT_TIME_SECONDS = 20
MAX_MESSAGES_PER_POLL = 10
VISIBILITY_TIMEOUT = int(os.getenv("VISIBILITY_TIMEOUT", "60"))


class GracefulShutdown:
    """Flips `should_stop` on SIGTERM so Fargate scale-in drains cleanly.

    ECS sends SIGTERM and then waits (stopTimeout) before SIGKILL, so
    finishing the in-flight message here avoids re-delivering work.
    """

    def __init__(self):
        self.should_stop = False
        signal.signal(signal.SIGTERM, self._handle)
        signal.signal(signal.SIGINT, self._handle)

    def _handle(self, signum, _frame):
        logger.info("received signal %s, finishing in-flight work", signum)
        self.should_stop = True


def _fingerprint_from_s3(s3_key: str) -> list[tuple[int, int]]:
    """Download audio from `audio-payloads`, normalize it, and fingerprint it.

    Imported lazily so the module remains importable (and unit-testable)
    on machines without the compiled C++ extension.
    """
    import fingerprint_engine

    from backend.services.audio_loader import load_wav_as_floats
    from backend.services.preprocesser import preprocess_audio

    with tempfile.TemporaryDirectory() as tmpdir:
        raw_path = os.path.join(tmpdir, "raw_input")
        wav_path = os.path.join(tmpdir, "normalized.wav")

        get_s3_client().download_file(AUDIO_BUCKET, s3_key, raw_path)
        preprocess_audio(raw_path, wav_path)
        samples = load_wav_as_floats(wav_path)

        return fingerprint_engine.fingerprint_audio(samples)


def process_message(body: dict, matcher: Matcher) -> dict:
    """Turn one queue message into a match payload."""
    request_id = body.get("requestId")

    if "fingerprints" in body:
        fingerprints = [(int(h), int(o)) for h, o in body["fingerprints"]]
    elif "s3Key" in body:
        fingerprints = _fingerprint_from_s3(body["s3Key"])
    else:
        raise ValueError("message must contain either 'fingerprints' or 's3Key'")

    matches = matcher.match(fingerprints)

    return {
        "requestId": request_id,
        "matched": bool(matches),
        "results": [m.to_dict() for m in matches],
    }


def run() -> None:
    """Poll SQS until told to stop."""
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    if not MATCH_QUEUE_URL:
        raise RuntimeError("MATCH_QUEUE_URL is not set")

    sqs = get_sqs_client()
    matcher = Matcher()
    lifecycle = GracefulShutdown()

    logger.info("matching-container polling %s", MATCH_QUEUE_URL)

    while not lifecycle.should_stop:
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

    logger.info("matching-container shut down cleanly")


if __name__ == "__main__":
    run()
