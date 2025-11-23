from fastapi import APIRouter, Depends, HTTPException, status, Request
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import google.genai as genai
import json
import os
from config import settings


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

deepgram = DeepgramClient(settings.DEEPGRAM_ENV_KEY)
genai.configure(apk_key = settings.GEMINI_APK_KEY)

router = APIRouter(prefix="/api", tags=['api'])

async def transcribe_audio(audio_data: bytes, target_language: str='en'):
    try:
        # v3 uses different way to send requests, matching that 
        response = deepgram.listen.v1.media.transcribe_file(
            request= audio_data, 
            model= 'nova-2',
            smart_format=True,
            language=target_language if target_language != "auto" else "en",
            detect_language=True if target_language == "auto" else False,
            punctuate=True,
        )
        
        transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
        confidence = response['results']['channels'][0]['alternatives'][0]['confidence']

        # Handle language detection
        if target_language == "auto" and hasattr(response.results.channels[0], 'detected_language'):
            detected_lang = response.results.channels[0].detected_language
        else:
            detected_lang = target_language
        
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
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        prompt = f"""You are a supportive language teacher. A student is learning {language} and said:
        "{text}"

        Analyze their speech and return a JSON object with:
        1. "corrected_text": The grammatically perfect version IN THE SAME LANGUAGE ({language}). Fix grammar/pronunciation but keep it in {language}!

        CRITICAL RULES:
        - "corrected_text" MUST be in {language}, NOT English
        - If they spoke Spanish, correct it to perfect Spanish
        - If they spoke French, correct it to perfect French
        - Never translate to English - only fix grammar in their target language
        - If already perfect, use "corrected_text" as-is and return it
        - Keep the corrected text natural and conversational

        Return ONLY valid JSON, no markdown or extra text."""
        
        response = model.generate_content(
            prompt,
            generation_config = genai.GenerationConfig(
                temperature = 0.7,
                max_output_tokens = 500,
                response_mime_time = "application/json"
            )
        )
        generated_text = response.text.strip()

        # Clean any markdowns if present. Naive markdown checking
        if generated_text.startswith("```json"):
            generated_text = generated_text[7:]
        if generated_text.startswith("```"):
            generated_text = generated_text[3:]
        if generated_text.endswith("```"):
            generated_text = generated_text[:-3]

        correction_data = json.loads(generated_text.strip())
        return correction_data

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Error while correction model was parsin json. {str(e)}")
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
        correction = await get_correction(text=transcription['text'], language=target_lang)

    
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with practice mode {str(e)}")
