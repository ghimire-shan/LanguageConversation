import os
from pathlib import Path
from typing import Optional

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    # Try to load .env from backend directory or current directory
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print(f"✅ Loaded .env from: {env_path}")
    else:
        # Fallback to current directory
        load_dotenv(override=True)
        print(f"✅ Loaded .env from current directory")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables only")
except Exception as e:
    print(f"⚠️ Error loading .env file: {e}")

class Settings:
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")
    
    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Server Configuration
    SERVER_URL: str = os.getenv("SERVER_URL", "http://localhost:8000")

    # Get keys for the models to run
    # Use getenv with explicit None check and strip whitespace
    _deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    DEEPGRAM_API_KEY = _deepgram_key.strip() if _deepgram_key else ""
    
    _google_key = os.getenv("GOOGLE_API_KEY")
    GOOGLE_API_KEY = _google_key.strip() if _google_key else ""
    
    _fish_key = os.getenv("FISH_AUDIO_API_KEY")
    FISH_AUDIO_API_KEY = _fish_key.strip() if _fish_key else ""
    
    # Debug: Check if keys are loaded (without exposing full keys)
    if DEEPGRAM_API_KEY:
        print(f"✅ DEEPGRAM_ENV_KEY loaded (length: {len(DEEPGRAM_API_KEY)})")
    else:
        print("⚠️ DEEPGRAM_ENV_KEY is empty or not set")
    
    if GOOGLE_API_KEY:
        print(f"✅ GOOGLE_API_KEY loaded (length: {len(GOOGLE_API_KEY)})")
    else:
        print("⚠️ GOOGLE_API_KEY is empty or not set")
    
    if FISH_AUDIO_API_KEY:
        print(f"✅ FISH_AUDIO_API_KEY loaded (length: {len(FISH_AUDIO_API_KEY)})")
    else:
        print("⚠️ FISH_AUDIO_API_KEY is empty or not set")

settings = Settings()

