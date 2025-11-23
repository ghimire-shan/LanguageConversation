from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
import json
import base64
import os
from google import genai
from google.genai import types
from routers.practice import transcribe_audio, generate_speech
from schemas.tts import TTSRequest
from schemas.conversation import Message
from config import settings

# Configure Google GenAI API key
# The new SDK reads from GEMINI_API_KEY environment variable
if settings.GOOGLE_API_KEY:
    os.environ['GEMINI_API_KEY'] = settings.GOOGLE_API_KEY
    print(f"GEMINI_API_KEY set (length: {len(settings.GOOGLE_API_KEY)})")
else:
    print("GOOGLE_API_KEY is empty! Check your .env file.")

# Create a single client object (reused across requests)
client = genai.Client()

router = APIRouter(prefix="/api", tags=['api'])

async def get_reply(user_message: str, conversation_history: list, language: str):
    """
    Generate a conversational reply using Gemini AI.
    
    Args:
        user_message: The current user message
        conversation_history: List of previous messages (last few for context)
        language: Target language code (e.g., 'es', 'fr', 'en')
    
    Returns:
        dict with 'reply' key containing the AI's response
    """
    try:
        print("2 here?")
        # Build conversation context from recent messages (last 5-10 messages)
        # Limit to last 10 messages to avoid token limits
        recent_messages = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
        
        # Build conversation context string
        conversation_context = ""
        for msg in recent_messages:
            role = msg.get('role', 'user') if isinstance(msg, dict) else msg.role
            content = msg.get('content', '') if isinstance(msg, dict) else msg.content
            if role == 'user':
                conversation_context += f"User: {content}\n"
            elif role == 'assistant':
                conversation_context += f"Assistant: {content}\n"
        
        # Add current user message
        conversation_context += f"User: {user_message}\n"
        print(conversation_context)
        
        # Language name mapping
        lang_names = {
            'es': 'Spanish',
            'fr': 'French',
            'en': 'English',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ja': 'Japanese',
            'zh': 'Chinese',
            'ko': 'Korean'
        }
        lang_name = lang_names.get(language, language)
        
        prompt = f"""You are a friendly and engaging conversation partner helping someone practice {lang_name}. 
You are having a natural, back-and-forth conversation with them in {lang_name}.

Previous conversation:
{conversation_context}

Your task:
- Respond naturally and conversationally in {lang_name}
- Keep your response appropriate to the conversation context
- Be helpful, friendly, and engaging
- Keep responses concise (1-3 sentences typically)
- Respond ONLY in {lang_name}, never in English
- If they ask a question, answer it naturally
- If they make a statement, respond appropriately (agree, ask follow-up, share related thought, etc.)

Return ONLY a JSON object with this exact format:
{{"reply": "your response in {lang_name}"}}

Do not include any markdown, explanations, or extra text. Only return the JSON."""

        # Use the new SDK format
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=200,
                response_mime_type='application/json'
            )
        )
        
        generated_text = response.text.strip()
        
        # Clean any markdown if present
        if generated_text.startswith("```json"):
            generated_text = generated_text[7:]
        if generated_text.startswith("```"):
            generated_text = generated_text[3:]
        if generated_text.endswith("```"):
            generated_text = generated_text[:-3]
        
        reply_data = json.loads(generated_text.strip())
        return reply_data
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing reply from model: {str(e)}"
        )
    except Exception as e:
        # Log the full error for debugging
        error_msg = str(e)
        error_type = type(e).__name__
        print(f"❌ Gemini API Error: {error_type}: {error_msg}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error generating reply: {error_type}: {error_msg}"
        )

@router.post('/reply')
async def conversation_reply(
    file: UploadFile = File(...),
    target_lang: str = Form(...),
    model_id: str = Form(...),
    chat_history: str = Form(None)  # JSON string of conversation history
):
    """
    Handle conversation reply endpoint.
    
    Accepts:
    - file: Audio file with user's speech
    - target_lang: Language code (e.g., 'es', 'fr')
    - model_id: Voice model ID (preset or user's cloned voice)
    - chat_history: JSON string of recent conversation history from frontend
    """
    try:
        audio_data = await file.read()

        if len(audio_data) < 1000:
            raise HTTPException(status_code=400, detail="Audio file is too small or empty")

        # Step 1: Transcribe audio to text
        transcription = await transcribe_audio(audio_data, target_lang)
        
        if not transcription['text'].strip():
            raise HTTPException(status_code=400, detail="No speech was detected")
        
        user_message = transcription['text']
        
        # Step 2: Parse chat history if provided
        conversation_history = []
        if chat_history:
            try:
                history_data = json.loads(chat_history)
                # Convert to list of Message objects or dicts
                if isinstance(history_data, list):
                    conversation_history = history_data
                elif isinstance(history_data, dict) and 'messages' in history_data:
                    conversation_history = history_data['messages']
            except json.JSONDecodeError:
                # If chat_history is invalid JSON, start with empty history
                conversation_history = []
        
        # Step 3: Generate conversational reply using Gemini
        reply = await get_reply(
            user_message=user_message,
            conversation_history=conversation_history,
            language=target_lang
        )

        # Step 4: Convert reply to speech using Fish Audio
        request = TTSRequest(transcript=reply['reply'], model_id=model_id)
        reply_audio = await generate_speech(request=request)

        # Step 5: Convert audio bytes to base64 for frontend
        audio_base64 = base64.b64encode(reply_audio).decode('utf-8')

        return {
            "success": True,
            "user_message": user_message,
            "reply_text": reply['reply'],
            "reply_audio": audio_base64,
            "audio_format": "wav"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating a response: {str(e)}")