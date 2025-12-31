"""
    this is the middleware for communication between the NestJS server and 
    this server(FastAPI) by API_KEY
"""
# fastapi_app/middleware.py
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os


API_KEY_NAME = "X-Internal-API-Key"
API_KEY = os.getenv("API_KEY")

# extract the API key from the header
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header  
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid or missing API Key"
    )

# How to use it in an endpoint
# @app.post("/qa", dependencies=[Depends(get_api_key)])
# async def qa_endpoint(...): ...