import os
from dotenv import load_dotenv
from fishaudio import FishAudio
from fishaudio.utils import save

def main():
    # Load environment variables from .env (for FISH_API_KEY)
    load_dotenv()

    voice_id = os.getenv("VOICE_ID")
    api_key = os.getenv("FISH_API_KEY")
    if not api_key:
        print("❌ ERROR: Missing FISH_API_KEY in .env file")
        return

    # Create Fish Audio client
    client = FishAudio(api_key=api_key)

    # TODO: put your saved voice ID here
    ###VOICE_ID = "629e083e56904688895b9962283e381b"

    print("\n🔊 Step 2: Generating TTS with your cloned voice...")

    # Generate speech using your saved voice model
    audio = client.tts.convert(
        text="Hola, soy la voz clonada de Gabriel. "
    "Estoy probando el sistema de texto a voz para ver qué tan natural sueno en español. "
    "En este momento estoy leyendo un mensaje bastante largo para que puedas escuchar mi pronunciación, "
    "mi ritmo y mi entonación. "
    "Si todo funciona bien, podré usar esta voz para proyectos de programación, presentaciones, "
    "videos educativos y mucho más. "
    "Gracias por escuchar esta pequeña demostración.",
        reference_id=VOICE_ID,
    )

    output_file = "cloned_voice_output.wav"
    save(audio, output_file)

    print(f"🎉 Saved generated audio to: {output_file}")


if __name__ == "__main__":
    main()
