import os
from dotenv import load_dotenv
from fishaudio import FishAudio
from fishaudio.utils import save

load_dotenv()

# Load API key
API_KEY = os.getenv("FISH_API_KEY")

if not API_KEY:
    print("❌ ERROR: Missing FISH_API_KEY in .env file")
    exit()

# Create Fish Audio client
client = FishAudio(api_key=API_KEY)

print("🎤 Step 1: Creating voice clone...")

# Read your audio sample
with open("user_sample.wav", "rb") as f:
    voice = client.voices.create(
        title="My Voice",
        voices=[f.read()],
        description="Custom voice clone created via Python SDK"
    )

print("✅ Voice clone created successfully!")
print("🔑 Voice ID:", voice.id)
print("\n🎯 All done!")
