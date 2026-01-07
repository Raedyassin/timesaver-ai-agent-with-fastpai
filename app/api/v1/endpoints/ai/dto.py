from pydantic import BaseModel

class SummaryRequest(BaseModel):
    youtubeUrl: str

class SummaryResponse(BaseModel):
    video_metadata: dict
    summary: str
    transcript: str | None
    transcript_available: bool

class ChatRequest(BaseModel):
    question: str
    relative_parts_from_transcript: list|None
    last_few_message: list|None
    video_chat_session_id: str


class ChatResponse(BaseModel):
    answer: str
