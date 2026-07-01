"""
Fingerprint matching against `songs-db`.

Algorithm (standard Shazam-style offset voting):
  1. For each query hash, look up every (song, offset) that shares it.
  2. For each candidate, histogram (db_offset - query_offset).
  3. A true match produces a large spike in one bin -- the recording lines
     up at a constant time delta. False matches scatter across bins.
  4. Score = size of the tallest bin; confidence = that bin's share of the
     candidate's votes.

The `popular-songs` Redis cache sits in front of these lookups in the target
architecture, but is not wired up yet -- `_postings_for_hash` is the single
place it will slot into.

Author: Fernando Rivas Espinoza
"""

import logging
from collections import defaultdict

from backend.db import models

logger = logging.getLogger(__name__)

__all__ = ["Matcher", "MatchResult"]

# A candidate needs at least this many aligned hashes to count as a match.
MIN_ALIGNED_HASHES = 5


class MatchResult:
    """One scored candidate song."""

    def __init__(self, song_id: str, score: int, confidence: float, offset: int):
        self.song_id = song_id
        self.score = score
        self.confidence = confidence
        self.offset = offset

    def to_dict(self) -> dict:
        return {
            "song_id": self.song_id,
            "score": self.score,
            "confidence": round(self.confidence, 4),
            "offset": self.offset,
        }


class Matcher:
    """Matches query fingerprints against the fingerprint store."""

    def _postings_for_hash(self, hash_value: int) -> list[dict]:
        """Return [{songId, offset}] for one hash.

        A failed lookup degrades to an empty posting list rather than
        failing the whole match -- one unreadable hash out of hundreds
        should not sink the request.
        """
        try:
            items = models.query_by_hash(hash_value)
        except Exception:
            logger.warning("songs-db lookup failed for hash %s", hash_value, exc_info=True)
            return []

        return [
            {"songId": item["songId"], "offset": int(item["offset"])} for item in items
        ]

    def match(self, query_fingerprints: list[tuple[int, int]], top_k: int = 5) -> list[MatchResult]:
        """Score candidate songs for a list of (hash, offset) query fingerprints."""
        if not query_fingerprints:
            return []

        # song_id -> {offset_delta: vote_count}
        votes: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))

        for hash_value, query_offset in query_fingerprints:
            for posting in self._postings_for_hash(hash_value):
                delta = posting["offset"] - query_offset
                votes[posting["songId"]][delta] += 1

        results = []
        for song_id, delta_histogram in votes.items():
            best_delta, best_count = max(delta_histogram.items(), key=lambda kv: kv[1])
            if best_count < MIN_ALIGNED_HASHES:
                continue
            total_votes = sum(delta_histogram.values())
            results.append(
                MatchResult(
                    song_id=song_id,
                    score=best_count,
                    confidence=best_count / total_votes,
                    offset=best_delta,
                )
            )

        results.sort(key=lambda r: (r.score, r.confidence), reverse=True)
        return results[:top_k]
