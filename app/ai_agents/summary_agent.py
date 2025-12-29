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

def _get_summary_task( transcript_text: str , video_summary_agent: Agent ):
    return Task(
        description=f"""
        Summarize the following transcript by following this Requirements:
            - Summary language must be same for transcript
            - The summary should be clear and readable and captures all key points.
            - The summary will be show for user and used it in Q/A agent.
            - In each place you say transcript replace it by video or the speaker
            - and make the summary is good for user to show on screen

        transcript start =>>>>
        {transcript_text}
        transcript end =<<<<<
        """,
        expected_output="A clear, concise summary capturing key points",
        agent=video_summary_agent
    )

def run_summary_crew(transcript_text: str, llm: LLM = gemini_llm):
    """
        :param transcript_text: Description
        :type transcript_text: str
        :returns: Summary
        it do this:
            Generates a summary using CrewAI.
    """
    video_summary_agent = _get_summary_agent(llm)
    video_summary_task = _get_summary_task(transcript_text, video_summary_agent)
    summary_crew = Crew(
        agents=[video_summary_agent],
        tasks=[video_summary_task],
        process=Process.sequential,
    )
    summary_result = summary_crew.kickoff()
    final_summary = summary_result.raw if hasattr(summary_result, 'raw') else str(summary_result)

    return final_summary
