from .audio_loader import load_wav_as_floats
from .preprocesser import preprocess_audio
from fingerprint_runner import run_fingerprint
import boto3
import json


def lambda_handler(event):
        request = event["requestID"]
        audio_location = event["s3key"]

        preprocessed_path = preprocess_audio(audio_location)
        friendly_audio = load_wav_as_floats(preprocessed_path)
        result = run_fingerprint(friendly_audio)
        response = result.encode("utf-8")

        return response

