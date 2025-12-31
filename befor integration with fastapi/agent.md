# 🤖 AI Agent System Design (For YouTube Summarizer Project)

## 🧠 Project Goal
An AI service that can summarize a YouTube video and let users chat with it like a tutor.

Your FastAPI service will be **multi-agent**, where each agent has a **specific role**.  
We’ll design it in a way that’s **scalable, clean, and easy to extend later** (like CrowAI or CrewAI style).

---

## 🤖 Recommended Agents (Final Design)

You should start with **3 main agents** for your MVP — enough to make it smart, but still efficient.

Then, you can optionally add 2 more later.

---

### 🎥 1️⃣ VideoFetcher Agent
**Purpose:**  
Extract the transcript and metadata from YouTube.

**Input:**  
- YouTube video URL  

**Output:**  
- Transcript text  
- Video title, duration, channel name  

**Implementation notes:**  
- Use `youtube-transcript-api` or `pytube`
- Cache the result in Redis

**Example Output:**
```json
{ 
  "title": "AI Tutorial",
  "duration": "15:23",
  "transcript": "Welcome to this tutorial on artificial intelligence..."
}
```

---

### ✍️ 2️⃣ Summarizer Agent
**Purpose:**  
Turn transcript into a clean summary.

**Input:**  
- Transcript text  

**Output:**  
- Short summary, long summary, or bullet points  

**Implementation notes:**  
- Use LLM (Gemini, OpenAI, Claude, etc.)
- Allow style selection later (e.g. “educational”, “key points”, “funny”)
- Store summary in DB via NestJS callback

**Example Output:**
```json
{
  "summary": "This video explains how AI models learn from data...",
  "key_points": ["Machine learning basics", "Training data importance"]
}
```

---

### 💬 3️⃣ Tutor Agent
**Purpose:**  
Let the user **chat** with the summary like a tutor.

**Input:**  
- User question  
- Summary (context)  

**Output:**  
- Natural, contextual answer  

**Implementation notes:**  
- Keep conversation context in short-term memory (in Redis)
- Can cite summary parts in responses
- Uses same LLM but with “teacher” style prompts

**Example Conversation:**
```
User: "Explain the math part more."
Agent: "The video mentions that the model adjusts weights during training..."
```

---

## 🧠 (Optional) Expansion Agents (Phase 2)

### 🗂 4️⃣ Memory Agent
**Purpose:**  
Store long-term conversation context or user preferences.

**Input:**  
- User ID + conversation logs  
**Output:**  
- Retrieved memory context  

**Implementation:**  
- Store summary history in DB (through NestJS)
- Retrieve past context for same video

---

### 🕵️ 5️⃣ Analyzer Agent
**Purpose:**  
Detect video type and adjust summary tone.

**Example:**  
- If educational → structured notes  
- If music → key lyrics or meaning  
- If tech → code examples  

**Implementation:**  
Use simple text classification (LLM or keyword-based)

---

## 🧩 Agent Workflow Diagram

```
User
 ↓
Frontend
 ↓
NestJS (Main Service)
 ↓
FastAPI (AI Service)
 ├── VideoFetcher Agent → gets transcript
 ├── Summarizer Agent → creates summary
 └── Tutor Agent → chats with user about summary
```

---

## ⚙️ FastAPI Structure Example

```
/ai_service
 ├─ /agents
 │   ├─ video_fetcher.py
 │   ├─ summarizer.py
 │   ├─ tutor.py
 │   └─ __init__.py
 ├─ main.py
 ├─ routers/
 │   ├─ ai_router.py
 │   └─ internal.py
 ├─ /core
 │   ├─ llm_client.py
 │   └─ cache.py
 └─ requirements.txt
```

---

## 🧠 Agent Example Code Structure (Pseudo)

```python
# summarizer_agent.py
from core.llm_client import LLMClient

class SummarizerAgent:
    def __init__(self):
        self.llm = LLMClient()

    async def summarize(self, transcript: str) -> dict:
        prompt = f"Summarize this transcript clearly:\n{transcript[:4000]}"
        summary = await self.llm.generate(prompt)
        return {"summary": summary}
```

---

## 🧩 Recommended Agent Count (Final)

| Agent | MVP | Future |
|--------|------|--------|
| 🎥 VideoFetcher | ✅ | ✅ |
| ✍️ Summarizer | ✅ | ✅ |
| 💬 Tutor | ✅ | ✅ |
| 🧠 Memory | ❌ | Optional later |
| 🕵️ Analyzer | ❌ | Optional later |

✅ **Total for MVP:** **3 agents**  
⏳ **Later (Phase 2):** add 2 more for context + personalization
