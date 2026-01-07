from .dto import SummaryRequest, SummaryResponse, ChatRequest, ChatResponse
from .service import generate_summary, chat_with_video
from app.api.v1.endpoints.middleware.communication import get_api_key
from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/summary", dependencies=[Depends(get_api_key)] , response_model=SummaryResponse)
async def summary(request: SummaryRequest):
  """
    Accepts a YouTube video URL and generates a summary.
  """
  return await generate_summary(request.youtubeUrl)


@router.post("/ask-question",dependencies=[Depends(get_api_key)] , response_model=ChatResponse)
async def chat(request: ChatRequest):
  """
    Accepts a question and video_id.
  """

  return await chat_with_video(
    request.video_chat_session_id,
    request.question, 
    request.relative_parts_from_transcript, 
    request.last_few_message
  )

