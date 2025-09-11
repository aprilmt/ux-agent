"""
Custom Middleware for the UX AI Agent
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import logging

logger = logging.getLogger(__name__)

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    # Simple rate limiting - in production, use Redis or similar
    # For now, just log the request
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Request processed in {process_time:.4f}s")
    
    return response

async def auth_middleware(request: Request, call_next):
    """Authentication middleware for protected routes"""
    # Skip auth for public endpoints
    public_paths = ["/", "/health", "/docs", "/openapi.json", "/api/auth/login", "/api/auth/register"]
    
    if request.url.path in public_paths:
        return await call_next(request)
    
    # Check for authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing or invalid authorization header"}
        )
    
    return await call_next(request)
