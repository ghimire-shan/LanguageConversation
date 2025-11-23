from pydantic import BaseModel, Field
from typing import List, Optional

class Message(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class ConversationRequest(BaseModel):
    messages: List[Message] = Field(..., description="Recent conversation history (last few messages)")
    language: str = Field(..., description="Language code (e.g., 'es', 'fr', 'en')")

