#!/usr/bin/env python3
"""
Simple LLM-powered backend for UX AI Agent
Uses OpenAI API with fallback to mock responses
"""

import os
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="UX AI Agent - Simple LLM Backend", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UXAgentRequest(BaseModel):
    message: str
    agent_type: str = "triage"

class UXAgentResponse(BaseModel):
    response: str
    agent_used: str
    knowledge_sources: list
    conversation_id: int

# Mock responses for testing
MOCK_RESPONSES = {
    "workflow": "I'm your UX Workflow Specialist! I can help you optimize design processes, implement user research methodologies, and improve cross-functional collaboration. What specific workflow challenge are you facing?",
    "thinking": "I'm your UX Strategic Thinker! I specialize in user psychology, strategic planning, and aligning UX with business goals. How can I help you develop a deeper understanding of your users?",
    "writing": "I'm your UX Writing Expert! I help create clear, effective content and microcopy that guides users and improves their experience. What writing challenge can I help you with?",
    "triage": "I've analyzed your request and recommend consulting with our UX specialists. Based on your question, I suggest:\n1) For process and workflow questions → UX Workflow Specialist.\n2) For strategic and user psychology questions → UX Strategic Thinker.\n3) For content and writing questions → UX Writing Expert.\n\nWould you like me to connect you with a specific specialist?"
}

def get_llm_response(message: str, agent_type: str) -> str:
    """Generate response - currently using mock responses"""
    # For now, return mock responses
    # In production, this would call OpenAI API
    return MOCK_RESPONSES.get(agent_type, MOCK_RESPONSES["triage"])

# API Routes
@app.get("/")
async def root():
    return {"message": "UX AI Agent Simple LLM API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "UX AI Agent Simple LLM"}

@app.get("/api/ux-agent/agents")
async def get_agents():
    """Get available agents"""
    return {
        "agents": {
            "workflow": "UX Workflow Specialist - Process optimization and methodology",
            "thinking": "UX Strategic Thinker - Strategy and user psychology", 
            "writing": "UX Writing Expert - Content and microcopy",
            "triage": "UX Request Triage - Routes requests to appropriate specialists"
        }
    }

@app.post("/api/ux-agent/chat", response_model=UXAgentResponse)
async def chat_with_ux_agent(request: UXAgentRequest):
    """Chat with UX AI agent"""
    # Generate response
    response = get_llm_response(request.message, request.agent_type)
    
    # Create conversation record
    conversation_id = 1  # Simple ID for demo
    
    return UXAgentResponse(
        response=response,
        agent_used=request.agent_type,
        knowledge_sources=["UX Knowledge Base", "Mock LLM"],
        conversation_id=conversation_id
    )

if __name__ == "__main__":
    print("🚀 Starting UX AI Agent Simple LLM Backend...")
    print("📱 Frontend: http://localhost:8080")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🤖 Using Mock LLM responses (ready for OpenAI integration)")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
