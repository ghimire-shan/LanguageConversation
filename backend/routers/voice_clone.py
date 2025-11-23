import os
from dotenv import load_dotenv
from fishaudio import FishAudio
from fishaudio.utils import save
from fastapi import APIRouter, Depends, HTTPException, status, Request
from config import settings

fish_audio = FishAudio(settings.FISH_AUDIO_API_KEY)
router = APIRouter(prefix="/api", tags=['api'])

@router.post("/create_clone")
async def create_user_clone(file):
    try:
        with open(file, "rb") as f:
            voice = fish_audio.voices.create(
            title="My Voice",
            voices=[f.read()],
            description="Custom voice clone created via Python SDK"
        )
        return {'voice_id': voice.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while creating user clone")
