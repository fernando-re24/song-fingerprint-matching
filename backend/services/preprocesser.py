"""
Normalize input audio to mono 44.1khz 16-bit PCM
Author: Fernando Espinoza
"""

import subprocess


def preprocess_audio(input_path: str, output_path: str) -> str:
    """Convert any audio file to mono, 44100Hz, 16-bit PCM WAV, trimmed to 15 seconds."""
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ac", "1",
        "-ar", "44100",
        "-acodec", "pcm_s16le",
        "-t", "15",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path
