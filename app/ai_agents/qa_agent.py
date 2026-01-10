from app.configs import gemini_llm
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool # Import decorator from CrewAI
from app.configs import redis_client
import json

# tools
@tool("Fetches Full Transcript from Redis")
def _get_full_transcript(session_id: str) -> str:
    """
        Use this tool ONLY when the user asks to SUMMARIZE or RE-SUMMARIZE the video.
        Do NOT use this for specific questions.
    """
    
    # ✅ 2. Match the Key Format used in NestJS
    # NestJS: `${videoChatSession.id}-metadata`
    key = f"{session_id}-metadata"

    # 3. Get the raw data
    data = redis_client.get(key)
    
    if not data:
        return "Error: Could not find transcript in Redis. The session ID might be wrong or data expired."
    
    # ✅ 4. Parse the JSON string
    # NestJS sent an object like: { transcript: "...", summary: "..." }
    # Redis returns this as a STRING, so we need to turn it back into a Dictionary.
    try:
        parsed_data = json.loads(data)
        
        # Extract just the transcript part
        transcript_text = parsed_data.get("transcript")
        
        if not transcript_text:
            return "Error: Found data, but 'transcript' field was empty."
            
        return transcript_text
        
    except json.JSONDecodeError:
        return "Error: Retrieved data was not valid JSON."

def _get_qa_agent(llm):
    return Agent(
        name="VideoQnA",
        role="Question Answering Agent, and the answer must be in the same language of the question",
        goal="Answer user questions based ONLY on the transcript and summary.",
        backstory="An expert assistant specialized in retrieving information from video transcripts.",
        llm=llm,
        tools=[_get_full_transcript],
        verbose=False, # Set to True for verbose logging
    )

def _get_qa_task(
    session_id: str,
    question: str,
    relative_parts_from_transcript: list[str],
    last_few_message: list[str],
    qa_agent: Agent 
) -> Task:
    
    # 1. Construct the Context String (RAG)
    context_text = "\n\n---\n\n".join(relative_parts_from_transcript)

    # 2. Construct the History String (Memory)
    conversation_history = "\n".join(last_few_message)

    description = f"""
    You are a Video Assistant. You have access to a tool: 'Fetches Full Transcript from Redis'.

    **INSTRUCTIONS:**
    1. **Language:** Answer in exact same language as user's question.
    2. **Handling "SUMMARIZE" Requests:**
        - If user asks to Summarize, Re-summarize, or Rewrite summary:
            - **USE THE TOOL 'Fetches Full Transcript from Redis'**.
            - Call tool with session_id: "{session_id}".
            - Use the returned full text to generate the summary.
        - DO NOT rely only on the provided chunks below.
    3. **Handling "Q&A" Requests:**
        - If user asks a specific question (e.g., "What is Docker?"):
            - DO NOT use the tool.
            - Answer using "CONTEXT FROM VIDEO" below.
            - If chunks don't contain definition, explain it yourself.
    4. **Out of Scope:** If question is unrelated, say you can't help.

    **SESSION ID:** {session_id}

    **CONTEXT FROM VIDEO (Use this for Q&A):**
    {context_text}

    **CONVERSATION HISTORY:**
    {conversation_history}

    **CURRENT REQUEST:**
    {question}

    Based on request type, decide to use tool or chunks.
    """

    return Task(
        description=description,
        expected_output="A clear, accurate answer in the same language as the user's question or summary.",
        agent=qa_agent
    )

def run_qa_crew(
        session_id: str,
        question: str,
        relative_parts_from_transcript: list[str],
        last_few_message: list[str],
        llm: LLM = gemini_llm
    ):
    qa_agent = _get_qa_agent(llm)
    qa_task = _get_qa_task(
        session_id,
        question, 
        relative_parts_from_transcript, 
        last_few_message, 
        qa_agent
    )
    qa_crew = Crew(
        agents=[qa_agent],
        tasks=[qa_task],
        process=Process.sequential,
    )

    qa_result = qa_crew.kickoff()
    metrics = qa_result.usage_metrics

    final_answer = qa_result.raw if hasattr(qa_result, 'raw') else str(qa_result)

    return {
        'llm_model': qa_agent.llm.model,
        'answer':final_answer,   
        'input_tokens': metrics.prompt_tokens, 
        'output_tokens':metrics.completion_tokens
    }
