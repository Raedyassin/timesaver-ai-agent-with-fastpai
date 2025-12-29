from fastapi import APIRouter
from .endpoints.ai.controller import router as ai_router
router = APIRouter()

router.include_router(ai_router, prefix="/ai")
