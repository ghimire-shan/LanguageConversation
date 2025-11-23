import json
from pathlib import Path
from typing import Dict, Optional

# Path to preset voices JSON file
PRESET_VOICES_PATH = Path(__file__).parent.parent / "preset_voices.json"

def load_preset_voices() -> Dict:
    """Load preset voices from JSON file"""
    try:
        with open(PRESET_VOICES_PATH, 'r') as f:
            data = json.load(f)
            return data.get('preset_voices', {})
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def get_preset_voice_id(voice_key: str) -> Optional[str]:
    """Get preset voice ID by key (e.g., 'energetic_male', 'adam', 'bro')"""
    presets = load_preset_voices()
    voice = presets.get(voice_key)
    if voice:
        return voice.get('id')
    return None

def is_preset_voice(model_id: str) -> bool:
    """Check if a model_id is a preset voice"""
    presets = load_preset_voices()
    for voice in presets.values():
        if voice.get('id') == model_id:
            return True
    return False

def get_all_preset_voices() -> Dict:
    """Get all preset voices with their details"""
    return load_preset_voices()

