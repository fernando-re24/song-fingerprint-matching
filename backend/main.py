"""
Main module for the backend of the audio fingerprint matching app.
Author: Fernando Rivas Espinoza
"""

import ffmpeg
import motor.motor_asyncio as motor
import numpy as np
import pybind11 as pb
from fastapi import FastAPI, File, UploadFile

app = FastAPI()


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
    }
