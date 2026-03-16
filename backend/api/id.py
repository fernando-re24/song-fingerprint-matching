"""
API endpoint for recive audio files from the frontend and send back matching results.
Author: Fernando Rivas Espinoza
"""

from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

@router.post("/identify")
async def identify_song(file: UploadFile = File(...)):
