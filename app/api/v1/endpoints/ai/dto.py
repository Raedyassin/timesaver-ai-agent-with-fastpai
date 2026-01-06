from pydantic import BaseModel

class SummaryRequest(BaseModel):
    youtubeUrl: str

class SummaryResponse(BaseModel):
    video_metadata: dict
    summary: str
    transcript: str | None
    transcript_available: bool

class ChatRequest(BaseModel):
    video_id: str
    question: str

class ChatResponse(BaseModel):
    answer: str
