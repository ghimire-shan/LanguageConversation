from fastapi import APIRouter, Depends, HTTPException, status, Request
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import google.genai as genai
import json
import os
from config import settings
from practice import transcribe_audio

router = APIRouter(prefix="/api", tags=['api'])
# conversation_window = 

@router.post('/reply')
async def conversation_reply(file, target_lang, clone):
    try:
        audio_data = await file.read()

        if len(audio_data) < 1000:
            raise HTTPException(status_code=400, detail="Audio file is too small or empty")

        # Step 1 is to transcribe with deepgram
        transcription = await transcribe_audio(audio_data, target_lang)

        # Step 2 is to check 
 
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating a response")