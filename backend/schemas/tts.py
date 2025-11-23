from pydantic import BaseModel, Field

class TTSRequest(BaseModel):
    transcript: str = Field(..., description="The text to convert to speech")
    model_id: str = Field(..., description="The Fish Audio cloned voice model ID (the ID of your custom voice clone)")