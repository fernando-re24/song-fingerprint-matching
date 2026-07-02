"""
Batch ingestion script for populating `songs-db` with songs.

Iterates over audio files in a directory, normalizes them, generates
fingerprints via the C++ engine, and writes song metadata + fingerprint
items into DynamoDB.

Usage:
    python -m scripts.ingest                          # default: datasets/songs/
    python -m scripts.ingest /path/to/songs/folder

Requires AWS credentials in the environment (or an instance/task role) and
SONGS_TABLE_NAME pointing at the target table.

Author: Fernando Rivas Espinoza
"""

import os
import sys
import tempfile
import uuid

# Add project root to path so imports work when run as a script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fingerprint_engine

from backend.db import models
from backend.db.index import create_fingerprint, create_song
from backend.services.audio_loader import load_wav_as_floats
from backend.services.preprocesser import preprocess_audio

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}


def parse_filename(filepath: str) -> tuple[str, str]:
    """Extract artist and title from filename.

    Expected format: 'Artist - Title.ext'
    Falls back to filename as title with 'Unknown' artist.
    """
    basename = os.path.splitext(os.path.basename(filepath))[0]
    if " - " in basename:
        artist, title = basename.split(" - ", 1)
        return artist.strip(), title.strip()
    return "Unknown", basename.strip()


def ingest_song(filepath: str) -> None:
    """Process a single audio file and write its fingerprints to DynamoDB."""
    artist, title = parse_filename(filepath)
    filename = os.path.basename(filepath)

    if models.song_exists(title, artist):
        print(f"  Skipping (already ingested): {artist} - {title}")
        return

    tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp_wav.close()

    try:
        preprocess_audio(filepath, tmp_wav.name)
        samples = load_wav_as_floats(tmp_wav.name)

        fingerprints = fingerprint_engine.fingerprint_audio(samples)

        if not fingerprints:
            print(f"  Warning: No fingerprints generated for {artist} - {title}")
            return

        song_id = str(uuid.uuid4())

        # Fingerprints first: a song row without fingerprints would be
        # matchable-but-empty, whereas orphan fingerprints are inert.
        fp_items = [
            create_fingerprint(hash_value=h, song_id=song_id, offset=offset)
            for h, offset in fingerprints
        ]
        models.put_fingerprints(fp_items)
        models.put_song(create_song(song_id, title, artist, filename))

        print(f"  Ingested: {artist} - {title} ({len(fingerprints)} fingerprints)")

    finally:
        os.unlink(tmp_wav.name)


def main():
    if len(sys.argv) > 1:
        songs_dir = sys.argv[1]
    else:
        songs_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "datasets",
            "songs",
        )

    if not os.path.isdir(songs_dir):
        print(f"Error: Directory not found: {songs_dir}")
        sys.exit(1)

    audio_files = sorted(
        os.path.join(songs_dir, f)
        for f in os.listdir(songs_dir)
        if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
    )

    if not audio_files:
        print(f"No audio files found in {songs_dir}")
        print(f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}")
        sys.exit(1)

    print(f"Found {len(audio_files)} audio file(s) in {songs_dir}\n")

    success_count = 0
    for i, filepath in enumerate(audio_files, 1):
        print(f"[{i}/{len(audio_files)}] Processing: {os.path.basename(filepath)}")
        try:
            ingest_song(filepath)
            success_count += 1
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nDone. Successfully ingested {success_count}/{len(audio_files)} songs.")


if __name__ == "__main__":
    main()
