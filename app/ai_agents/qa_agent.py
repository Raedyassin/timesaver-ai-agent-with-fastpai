from app.configs import gemini_llm
from crewai import Agent, Task, Crew, Process, LLM
def _get_qa_agent(llm):
    return Agent(
        name="VideoQnA",
        role="Question Answering Agent, and the answer must be in the same language of the question",
        goal="Answer user questions based ONLY on the transcript and summary.",
        backstory="An expert assistant specialized in retrieving information from video transcripts.",
        llm=llm,
        verbose=False, # Set to True for verbose logging
    )

def _get_qa_task( question: str, transcript: str, summary: str, qa_agent: Agent ):
    return Task(
        description=f"""
        You will answer the user's question using ONLY the provided content.
        Your answer must:
            - The answer must be in the same language of the question language
            - Be accurate and based strictly on the Transcript and Summary.
            - Be clear and easy to understand.
            - Do NOT add information that was not in the video.
            - If the user asked about anything out of the video tell hem ask question related to the video (you response in good way)

        Question: {question}

        Transcript:
        {transcript}

        Summary:
        {summary}

        """,
        expected_output="A clear factual answer to the user question.",
        agent=qa_agent
    )

def run_qa_crew(question: str, transcript: str, summary: str,llm: LLM = gemini_llm):
    qa_agent = _get_qa_agent(llm)
    qa_task = _get_qa_task(question, transcript, summary, qa_agent)
    qa_crew = Crew(
        agents=[qa_agent],
        tasks=[qa_task],
        process=Process.sequential,
    )

    qa_result = qa_crew.kickoff()
    final_answer = qa_result.raw if hasattr(qa_result, 'raw') else str(qa_result)

    return final_answer
