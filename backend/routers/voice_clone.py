from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from fishaudio import FishAudio
from config import settings
import os

# FishAudio reads API key from environment variable FISH_API_KEY
os.environ['FISH_API_KEY'] = settings.FISH_AUDIO_API_KEY
fish_audio = FishAudio()
router = APIRouter(prefix="/api", tags=['api'])

@router.post("/create_clone")
async def create_user_clone(
    file: UploadFile = File(...),
    voice_name: str = Form(...),
):
    """
    Create or update a voice clone for the authenticated user.
    
    If the user already has a voice_model_id, it will be updated with the new voice.
    Otherwise, a new voice clone will be created and saved to the user's record.
    """
    try:
        # Read the audio file
        audio_data = await file.read()
        
        voice = fish_audio.voices.create(
            title=voice_name,
            voices=[audio_data],
            description=f"Custom voice clone for {"me"}"
        )
                
        return {
            "success": True,
            "message": "Voice clone updated successfully",
            "voice_id": voice.id,
            "voice_name": voice_name
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while creating/updating user clone: {str(e)}"
        )
