import os
from deepgram import DeepgramClient
from config import settings

def test_deepgram(audio_file_path: str, language: str = "en"):
    """
    Test Deepgram transcription with a local audio file
    
    Args:
        audio_file_path: Path to your audio file (WAV, MP3, WEBM, etc.)
        language: Language code (en, es, fr, etc.) or "auto" for auto-detection
    """
    print(f"\n{'='*60}")
    print(f"🎤 Testing Deepgram with: {audio_file_path}")
    print(f"{'='*60}\n")
    
    try:
        # Initialize Deepgram client
        deepgram = DeepgramClient(api_key=settings.DEEPGRAM_ENV_KEY)
        
        # Read audio file
        with open(audio_file_path, "rb") as audio_file:
            audio_data = audio_file.read()
        
        print(f"📁 File size: {len(audio_data)} bytes")
        print("🔄 Transcribing...")
        
        # Transcribe using v3+ SDK (simplified API)
        response = deepgram.listen.v1.media.transcribe_file(
            request=audio_data,
            model="nova-2",
            smart_format=True,
            language=language if language != "auto" else "en",
            detect_language=True if language == "auto" else False,
            punctuate=True,
        )
        
        # Extract results (v3+ has cleaner response structure)
        transcript = response.results.channels[0].alternatives[0].transcript
        confidence = response.results.channels[0].alternatives[0].confidence
        
        # Handle language detection
        if language == "auto" and hasattr(response.results.channels[0], 'detected_language'):
            detected_lang = response.results.channels[0].detected_language
        else:
            detected_lang = language
        
        # Display results
        print("\n" + "="*60)
        print("✅ TRANSCRIPTION SUCCESS!")
        print("="*60)
        print(f"\n📝 Transcript: {transcript}")
        print(f"\n🌍 Detected Language: {detected_lang}")
        print(f"📊 Confidence: {confidence:.2%}")
        print(f"\n{'='*60}\n")
        
        return {
            "success": True,
            "transcript": transcript,
            "language": detected_lang,
            "confidence": confidence
        }
        
    except FileNotFoundError:
        print(f"❌ Error: File not found: {audio_file_path}")
        return {"success": False, "error": "File not found"}
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def test_multiple_files(file_paths: list, language: str = "en"):
    """
    Test multiple audio files at once
    """
    print("\n" + "="*60)
    print(f"🎯 Testing {len(file_paths)} audio files")
    print("="*60)
    
    results = []
    for file_path in file_paths:
        result = test_deepgram(file_path, language)
        results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    successful = sum(1 for r in results if r.get("success"))
    print(f"✅ Successful: {successful}/{len(file_paths)}")
    print(f"❌ Failed: {len(file_paths) - successful}/{len(file_paths)}")
    print("="*60 + "\n")


if __name__ == "__main__":
    # ========================================
    # EDIT THIS SECTION WITH YOUR FILES
    # ========================================
    
    # Option 1: Test a single file
    test_deepgram(
        audio_file_path="./data/Record (online-voice-recorder.com) (3).mp3",
        language="es"  # or "es", "fr", "auto", etc.
    )
    
    # Option 2: Test multiple files at once
    # test_multiple_files([
    #     "audio1.wav",
    #     "audio2.mp3",
    #     "spanish_audio.wav",
    # ], language="auto")
    
    # ========================================
    # SUPPORTED FORMATS
    # ========================================
    # WAV, MP3, WEBM, OGG, FLAC, M4A, AAC, etc.
    
    # ========================================
    # LANGUAGE CODES
    # ========================================
    # en = English
    # es = Spanish
    # fr = French
    # de = German
    # it = Italian
    # pt = Portuguese
    # zh = Chinese
    # ja = Japanese
    # ko = Korean
    # auto = Auto-detect