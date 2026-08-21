from fingerprinting_engine import compute_fft
from fingerprinting_engine import generate_spectrogram
from fingerprinting_engine import find_peaks
from fingerprinting_engine import fingerprint_audio
from fingerprinting_engine import generate_hashes


def hasharray_to_json(hashes):
    # TODO: Implement logic for making hashes into a valid json payloads

    return 

def run_fingerprint(audio):
    freq_domain = compute_fft(audio)
    spectrogram = generate_spectrogram(freq_domain)
    peaks = find_peaks(spectrogram)
    fingerprint = fingerprint_audio(peaks)
    hashes_raw = generate_hashes(fingerprint)

    return hasharray_to_json(hashes_raw)
