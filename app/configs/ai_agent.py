from crewai import LLM
import os
# Load API Key from environment variable
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

# Initialize the LLM for crewai
gemini_llm = LLM(model="gemini/gemini-2.5-flash-lite", temperature=0, api_key=api_key)


