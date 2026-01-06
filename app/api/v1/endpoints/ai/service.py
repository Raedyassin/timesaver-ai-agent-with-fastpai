from fastapi import HTTPException
from .dto import SummaryResponse, ChatResponse

# --- In-Memory Storage ---
# Stores video data: { "video_id": { "transcript": "...", "summary": "..." } }
from typing import Dict, Any
session_store: Dict[str, Dict[str, Any]] = {}

from app.utils.youtube import get_video_metadata_transcript
from app.ai_agents import run_summary_crew, run_qa_crew

async def generate_summary(url: str):
    """
        1. Fetches video info and transcript using utils.py.
        2. Generates a summary using CrewAI.
        3. Stores data in memory for chat.
    """
    # 1. Fetch Data from YouTube
    video_data = get_video_metadata_transcript(url)

    if video_data["metadata_error"]:
        raise HTTPException(status_code=400, detail=video_data["metadata_error"])
    
    if video_data["transcript_error"]:
        # We return metadata, but note that transcript failed
        return SummaryResponse(
            video_metadata = video_data["metadata"],
            summary="Could not generate summary because transcript is unavailable.",
            transcript=None,
            transcript_available=False
        )

    metadata = video_data["metadata"]
    transcript_text = video_data["transcript"]["text"]
    video_id = metadata["video_id"]

    # 2. Generate Summary with CrewAI
    try:
        summary = run_summary_crew(transcript_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

    # 3. Store in Session
    session_store[video_id] = {
        "transcript": transcript_text,
        "summary": summary,
        "title": metadata["title"]
    }

    return SummaryResponse(
        video_metadata=metadata,
        summary=summary,
        transcript=transcript_text, 
        transcript_available=True
    )

async def chat_with_video(video_id: str, question: str):
    """
      Accepts a question and video_id.
      Retrieves context from session_store and answers using CrewAI.
    """
    # 1. Check if video session exists
    if video_id not in session_store:
        raise HTTPException(status_code=404, detail="Video ID not found. Please call /summary first.")

    context = session_store[video_id]

    # 2. Run QA Agent
    try:
        final_answer = run_qa_crew(
            question=question, 
            transcript=context["transcript"], 
            summary=context["summary"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during chat processing: {str(e)}")

    return ChatResponse(answer=final_answer)

