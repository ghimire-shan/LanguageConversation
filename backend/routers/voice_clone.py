from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from fishaudio import FishAudio
from config import settings
from database import get_db
from models.user import User
from auth import get_current_user

fish_audio = FishAudio(settings.FISH_AUDIO_API_KEY)
router = APIRouter(prefix="/api", tags=['api'])

@router.post("/create_clone")
async def create_user_clone(
    file: UploadFile = File(...),
    voice_name: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or update a voice clone for the authenticated user.
    
    If the user already has a voice_model_id, it will be updated with the new voice.
    Otherwise, a new voice clone will be created and saved to the user's record.
    """
    try:
        # Read the audio file
        audio_data = await file.read()
        
        if len(audio_data) < 1000:
            raise HTTPException(
                status_code=400,
                detail="Audio file is too small. Please provide at least 10 seconds of clear audio."
            )
        
        # Check if user already has a voice model
        if current_user.voice_model_id:
            # User already has a voice model - update it
            try:
                # Create new voice clone (Fish Audio doesn't have update, so we create new)
                voice = fish_audio.voices.create(
                    title=voice_name or current_user.voice_name or "My Voice",
                    voices=[audio_data],
                    description=f"Custom voice clone for {current_user.email}"
                )
                
                # Update user's voice model ID and name in database
                current_user.voice_model_id = voice.id
                current_user.voice_name = voice_name
                db.commit()
                db.refresh(current_user)
                
                return {
                    "success": True,
                    "message": "Voice clone updated successfully",
                    "voice_id": voice.id,
                    "voice_name": voice_name
                }
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error updating voice clone: {str(e)}"
                )
        else:
            # User doesn't have a voice model - create new one
            try:
                voice = fish_audio.voices.create(
                    title=voice_name or "My Voice",
                    voices=[audio_data],
                    description=f"Custom voice clone for {current_user.email}"
                )
                
                # Save voice model ID and name to user's record
                current_user.voice_model_id = voice.id
                current_user.voice_name = voice_name
                db.commit()
                db.refresh(current_user)
                
                return {
                    "success": True,
                    "message": "Voice clone created successfully",
                    "voice_id": voice.id,
                    "voice_name": voice_name
                }
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error creating voice clone: {str(e)}"
                )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while creating/updating user clone: {str(e)}"
        )
