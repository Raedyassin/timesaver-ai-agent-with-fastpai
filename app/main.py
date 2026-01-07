from fastapi import FastAPI
from .api.v1.router import router as api_router
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="YouTube Video Agent API")

# Include the API router
app.include_router(api_router, prefix="/api/v1")



