from app.configs import gemini_llm
from crewai import Agent, Task, Crew, Process, LLM

def _get_summary_agent(llm):
    return Agent(
        role="""You are an AI agent that receives the transcript of a YouTube video and generates a concise Summary in his original language .Make it clear, structured, and include main points only.""",
        goal="""To Create a clear and readable summary that captures all key points of the transcript,
                to show it for user, and used it for conversation with llm in Q/A agent.""",
        backstory="we get the transcript for the video and pass it for you to make a clear and readable summary for user and Q/A agent later",
        llm=llm,
        verbose=False, # Set to True for verbose logging
    )

def _get_summary_task( transcript_text: str , video_summary_agent: Agent, summary_instruction: str | None = None):
    return Task(
        description=f"""
        Summarize the following transcript based on the user's requirements.

        1. **Language Rule (Critical):**
            - Check the "USER INSTRUCTIONS" section below.
           - **If INSTRUCTIONS are provided:** The summary **must** be in the exact same language as those instructions.
           - **If INSTRUCTIONS are "None" or empty:** The summary **must** be in the exact same language as the Transcript below.

        2. **Handling User Instructions (Safety):**
            - Read the "USER INSTRUCTIONS" carefully.
           - **If you can't understand the "CRITICAL USER INSTRUCTIONS":** Treat them as if they do not exist. Ignore them and proceed to summarize normally based on the transcript and language rules above.

        3. **Content & Clarity (Using Your Knowledge):**
            - The summary should capture all key points from the transcript.
           - **Crucial:** If the user instructions ask to "explain", "clarify", or "make it clear":
                - Identify technical terms or complex concepts mentioned in the transcript.
             - **Use your own internal knowledge** to provide brief, clear explanations or definitions for those terms.
                - Do NOT hallucinate or add completely new topics, only expand on what is already mentioned.

        4. **Formatting:**
            - Be clear and easy to read on a screen.
            - The summary will be shown to the user and the user will ask questions about the video.
            - Replace "transcript" with "video" or "the speaker".

        5. **USER INSTRUCTIONS:**
        {summary_instruction or "None"}

        6. **Transcript:**
        Transcript start =>>>>

        {transcript_text}
        
        Transcript end =<<<
        """,
        expected_output="A clear summary with additional explanations if requested.",
        agent=video_summary_agent
    )
def run_summary_crew(transcript_text: str,summary_instruction: str | None = None, llm: LLM = gemini_llm):
    """
        :param transcript_text: Description
        :type transcript_text: str
        :returns: Summary
        it do this:
            Generates a summary using CrewAI.
    """
    video_summary_agent = _get_summary_agent(llm)
    video_summary_task = _get_summary_task(transcript_text, video_summary_agent, summary_instruction)
    summary_crew = Crew(
        agents=[video_summary_agent],
        tasks=[video_summary_task],
        process=Process.sequential,
    )
    summary_result = summary_crew.kickoff()
    final_summary = summary_result.raw if hasattr(summary_result, 'raw') else str(summary_result)

    return final_summary
