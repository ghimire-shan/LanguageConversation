from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
import json
import base64
from routers.practice import transcribe_audio, generate_speech
from schemas.tts import TTSRequest

router = APIRouter(prefix="/api", tags=['api'])

async def get_reply(text, language):
    pass

@router.post('/reply')
async def conversation_reply(
    file: UploadFile = File(...),
    target_lang: str = Form(...),
    model_id: str = Form(...)
):
    try:
        audio_data = await file.read()

        if len(audio_data) < 1000:
            raise HTTPException(status_code=400, detail="Audio file is too small or empty")

        # Step 1 is to transcribe with deepgram
        transcription = await transcribe_audio(audio_data, target_lang)
        print(transcription)
        
        if not transcription['text'].strip():
            raise HTTPException(status_code=400, detail="No speech was detected")

        # Step 2 is to take the current reply and other "replies" and have the model generate a reply
        reply = await get_reply(text= transcription['text'], language = target_lang)
        # {reply: "..."}

        # Step 3 is to give it to a text to speech model i.e (Fish audio)
        request = TTSRequest(transcript= reply['reply'], model_id = model_id)
        reply_audio = await generate_speech(request= request)

        # Convert the audio to base64 for easy frontend implementation
        audio_base64 = base64.b64decode(reply_audio).decode('utf-8')

        return {
            "success": True,
            "reply_text": reply['reply'],
            "reply_audio": audio_base64,
            "audio_format": "wav"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating a response")