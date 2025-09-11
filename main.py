"""
UX AI Agent - Main Application Entry Point
Built with OpenAI Agents SDK and FastAPI
"""

import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import auth, ux_agent, payment, user
from app.services.ux_agent_service import UXAgentService

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await init_db()
    print("🚀 UX AI Agent started successfully!")
    yield
    # Shutdown
    print("👋 UX AI Agent shutting down...")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered UX workflow, thinking, and writing assistant for B2B enterprise",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(ux_agent.router, prefix="/api/ux-agent", tags=["UX Agent"])
app.include_router(payment.router, prefix="/api/payment", tags=["Payment"])
app.include_router(user.router, prefix="/api/user", tags=["User"])

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "UX AI Agent API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "UX AI Agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
