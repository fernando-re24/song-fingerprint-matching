"""
Load a normalized WAV file into a list of floats for the C++ fingerprinting engine.
Author: Fernando Espinoza
"""

import struct
import wave


def load_wav_as_floats(path: str) -> list[float]:
    """Read a 16-bit PCM WAV and return samples normalized to [-1.0, 1.0]."""
    with wave.open(path, "rb") as wf:
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    # Unpack 16-bit signed integers
    samples = struct.unpack(f"<{n_frames}h", raw)

    # Normalize to [-1.0, 1.0]
    return [s / 32768.0 for s in samples]
