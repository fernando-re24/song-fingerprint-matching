"""
Normalize input audio to mono 44.1khz 16-bit PCM
Author: Fernando Espinoza
"""

import ffmpeg

def preprocess_audio(input_path: str, output_path: str) -> None:
