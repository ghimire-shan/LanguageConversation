# Sonant-ai

Sonant-ai is a language learning/ conversation tool built for Madhacks 2025. We noticed that most language learning apps rely on memorization and hearing languages being spoken. A big drawback, we felt when learning languages are the lack of actual practice speaking the language. On top of that, many of us feel awkard or shy speaking the language in the first place. Sonant-ai was built to help people learn their language of choice and build confidence speaking the language.

## What it does
* Users are able to clone their voice using `fish-audio`'s voice cloning. A short 15 second clip is required to create a persistent voice model. We reuse the same model unless the user uplodas a new voice clone.
* Using their cloned voice, user's are able to **practice** a language of their choice. The practice mode allows user to say any sentence in a language of their choice, and they hear a grammatically correct version of their sentence in their own voice. We believe that being able to hear yourself speak a grammatically correct version of a language they are learning will motivate them towards achieving that grammatically correct version.
* Users can also choose to **communicate** in a language of their choice. Actual communication helps a lot during language learning so we wanted to allow the user's to freely communicate. In Communication mode, users choose a language and a model for the type of voice they want to hear back and have a free-flowing, natural, and contextually aware conversation.

## How it works
User is able to record a voice note. The voice note gets sent to the *transcribing layer*. A model, `deepgram nova-2` currently, converts it from speech to text. The text is sent to a logical core, `gemini-2.0-flash` currently, to either get a grammatically correct answer or a reply to their speech in the current language. The text is then sent to `fish-audio-s1` to convert from text to speech in the audio model of their choice. This is sent to the frontend for the user to hear

## Usage
1. Clone the repository
```bash
git clone <repository-url>
```
2. Set the environment variables by creating a `.env` file within backend
    * `GOOGLE_API_KEY`: Get from Google AI Studio
    * `FISH_AUDIO_API_KEY`: Get from Fish Audio
    * `DEEPGRAM_API_KEY`: Get from Deepgram
3. Run the backed, fastapi
```bash
cd backend
uvicorn main:app --reload
```
