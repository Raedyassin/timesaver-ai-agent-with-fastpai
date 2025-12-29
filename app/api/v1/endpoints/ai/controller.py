from .dto import SummaryRequest, SummaryResponse, ChatRequest, ChatResponse
from .service import generate_summary, chat_with_video

from fastapi import APIRouter

router = APIRouter()

@router.post("/summary", response_model=SummaryResponse)
async def summary(request: SummaryRequest):
  """
    Accepts a YouTube video URL and generates a summary.
  """
  return await generate_summary(request.url)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
  """
    Accepts a question and video_id.
  """
  return await chat_with_video(request.video_id, request.question)

