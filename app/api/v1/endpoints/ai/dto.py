from pydantic import BaseModel

class SummaryRequest(BaseModel):
    youtube_url: str
    summary_instruction: str | None = None # Optional summary instruction

class SummaryResponse(BaseModel):
    video_metadata: dict
    summary: str
    transcript: str | None
    transcript_available: bool
    input_tokens: int
    output_tokens: int
    llm_model: str


class ChatRequest(BaseModel):
    question: str
    relative_parts_from_transcript: list|None
    last_few_message: list|None
    video_chat_session_id: str


class ChatResponse(BaseModel):
    answer: str
    input_tokens: int
    output_tokens: int
    llm_model: str

