from fastapi import APIRouter, Depends, HTTPException, status, Request
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import google.genai as genai

import os


"""
    The routes for the practice gets a audio stream, language, and voice to use
        * Convert Audio to Text (STT) Model A
        Given the speech, check correctness and correct the sentence, 
        * Correct Sentence in the given language Model B
        * If the voice is of the User
            * Call the method that stores the users id in Fish audio
        * Convert the Text-to-Speech using the provided clone: Model C (Fish audio)
        Return audio stream to user
"""

deepgram = DeepgramClient(os.getenv("DEEPGRAM_ENV_KEY"))
genai.configure(apk_key = os.getenv('GEMINI_APK_KEY'))


router = APIRouter(prefix="/api", tags=['api'])

async def transcribe_audio(audio_data, target_language: str='en'):
    try:
        # Make the audio payload
        payload: FileSource = {
            "buffer": audio_data
        }

        # Give the transcription options
        options = PrerecordedOptions(
            model = 'nova-2',
            smart_format = True,
            language = target_language if target_language != "auto" else "en",
        )

        # Transcribe the thing we are given
        response = deepgram.listen.rest.v("1").transcribe_file(payload, options)

        # Extract the results
        result = response.to_dict()
        transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
        confidence = result['results']['channels'][0]['alternatives'][0]['confidence']
        
        return {
            'text': transcript,
            'confidence': confidence
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech to text {str(e)}")
    
async def get_correction(text, language):
    """
        Given a text in a certain language, use an LLM to check correctness of the sentence.
        If the sentence is not correct, make it correct
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"The correction model returned an error. {str(e)}")

    
@router.post("/practice")
async def practice_speech(file, target_lang, clone):

    try:
        audio_data = await file.read()

        if len(audio_data) < 1000:
            raise HTTPException(status_code=400, detail="Audio file is too small or empty")

        # Step 1 is to transcribe with deepgram
        transcription = await transcribe_audio(audio_data, target_lang)

        if not transcription['text'].strip():
            raise HTTPException(status_code=400, detail="No speech was detected")

        # Step 2 is to correct the audio

    
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with practice mode {str(e)}")
