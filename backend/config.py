import os
from pathlib import Path
from typing import Optional

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    # Try to load .env from backend directory or current directory
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Fallback to current directory
        load_dotenv()
except ImportError:
    pass

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
    DEEPGRAM_ENV_KEY = os.getenv("DEEPGRAM_ENV_KEY", "")
    GEMINI_APK_KEY = os.getenv("GEMINI_APK_KEY", "")
    FISH_AUDIO_API_KEY = os.getenv("FISH_AUDIO_API_KEY", "")

settings = Settings()

