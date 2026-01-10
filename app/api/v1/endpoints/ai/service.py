from fastapi import HTTPException
from .dto import SummaryResponse, ChatResponse

from app.utils.youtube import get_video_metadata_transcript
from app.ai_agents import run_summary_crew, run_qa_crew

async def generate_summary(url: str, summary_instruction: str | None = None):
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
        return SummaryResponse (
            video_metadata = video_data["metadata"],
            summary="Could not generate summary because transcript is unavailable.",
            transcript=None,
            transcript_available=False,
            input_tokens=0,
            output_tokens=0,
            llm_model=""
        )

    metadata = video_data["metadata"]
    transcript_text = video_data["transcript"]["text"]

    # 2. Generate Summary with CrewAI
    try:
        summary_crew_result = run_summary_crew(transcript_text, summary_instruction)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")
    print("Summary generated:", summary_crew_result)
    return SummaryResponse(
        video_metadata=metadata,
        summary=summary_crew_result["summary"],
        transcript=transcript_text, 
        transcript_available=True, 
        input_tokens=summary_crew_result['input_tokens'],
        output_tokens=summary_crew_result['output_tokens'],
        llm_model=summary_crew_result['llm_model'], # input_tokens, output_tokens
    )

async def chat_with_video(
    session_id: str,
    question: str,
    relative_parts_from_transcript: list[str],
    last_few_message: list[str]
    ):
    """
        Accepts a question and relative_parts_from_transcript and last_few_message 
        from NestJS server.
    """

    # 2. Run QA Agent
    try:
        final_answer_result = run_qa_crew(
            session_id=session_id,
            question=question,
            relative_parts_from_transcript=relative_parts_from_transcript, 
            last_few_message=last_few_message
        )
    except Exception as e:
        print(" Error during chat processing:", str(e))
        raise HTTPException(status_code=500, detail=f"AI serivce: Error during chat processing: {str(e)}")

    return ChatResponse(
        answer=final_answer_result['answer'], 
        input_tokens=final_answer_result['input_tokens'], 
        output_tokens=final_answer_result['output_tokens'], 
        llm_model=final_answer_result['llm_model']
    )

