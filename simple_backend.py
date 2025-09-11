#!/usr/bin/env python3
"""
Simple backend server for UX AI Agent
This is a minimal implementation for testing the frontend
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Simple in-memory storage for demo
users_db = {}
conversations_db = {}
current_user_id = 1

app = FastAPI(title="UX AI Agent - Simple Backend", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    full_name: str = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str = None
    is_active: bool = True
    is_premium: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UXAgentRequest(BaseModel):
    message: str
    agent_type: str = "triage"

class UXAgentResponse(BaseModel):
    response: str
    agent_used: str
    knowledge_sources: list = []
    conversation_id: int

class ConversationResponse(BaseModel):
    id: int
    title: str
    agent_type: str
    created_at: str
    messages: list = []

# Mock UX Agent responses
UX_AGENT_RESPONSES = {
    "workflow": {
        "greeting": "Hello! I'm your UX Workflow Specialist. I help optimize UX processes, implement best practices, and streamline design workflows for enterprise teams. How can I assist you with your UX workflow today?",
        "default": "For UX workflow optimization, I recommend: 1) Implementing user-centered design processes, 2) Establishing clear design systems, 3) Creating efficient handoff processes between design and development teams, 4) Setting up regular user testing cycles, and 5) Documenting UX guidelines and best practices."
    },
    "thinking": {
        "greeting": "Hello! I'm your UX Strategic Thinker. I specialize in strategic UX planning, user psychology, and aligning UX initiatives with business goals. What strategic UX challenge can I help you think through?",
        "default": "For strategic UX thinking, consider: 1) Understanding your users' mental models and motivations, 2) Aligning UX goals with business objectives, 3) Creating user personas based on real data, 4) Developing a UX vision that supports long-term business growth, and 5) Building empathy across your organization for user needs."
    },
    "writing": {
        "greeting": "Hello! I'm your UX Writing Expert. I help create clear, effective content and microcopy that guides users and improves their experience. What writing challenge can I help you with?",
        "default": "For effective UX writing: 1) Use clear, concise language that users understand, 2) Write in an active voice, 3) Be consistent with terminology across your product, 4) Write error messages that help users solve problems, 5) Create helpful tooltips and onboarding content, and 6) Test your copy with real users to ensure clarity."
    },
    "triage": {
        "greeting": "Hello! I'm your UX Request Triage agent. I'll help route your request to the most appropriate UX specialist. What would you like help with today?",
        "default": "I've analyzed your request and recommend consulting with our UX specialists. Based on your question, I suggest:\n1) For process and workflow questions → UX Workflow Specialist.\n2) For strategic and user psychology questions → UX Strategic Thinker.\n3) For content and writing questions → UX Writing Expert.\n\nWould you like me to connect you with a specific specialist?"
    }
}

def get_agent_response(message: str, agent_type: str) -> str:
    """Generate a mock response from the specified agent"""
    agent_responses = UX_AGENT_RESPONSES.get(agent_type, UX_AGENT_RESPONSES["triage"])
    
    # Simple keyword matching for demo
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["hello", "hi", "hey", "greeting"]):
        return agent_responses.get("greeting", agent_responses["default"])
    
    return agent_responses["default"]

# API Routes
@app.get("/")
async def root():
    return {"message": "UX AI Agent API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "UX AI Agent"}

@app.post("/api/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    global current_user_id
    
    # Check if user already exists
    for user in users_db.values():
        if user["email"] == user_data.email or user["username"] == user_data.username:
            raise HTTPException(status_code=400, detail="Email or username already registered")
    
    # Create new user
    user_id = current_user_id
    current_user_id += 1
    
    users_db[user_id] = {
        "id": user_id,
        "email": user_data.email,
        "username": user_data.username,
        "full_name": user_data.full_name,
        "is_active": True,
        "is_premium": False  # Demo: set to True for testing
    }
    
    return UserResponse(**users_db[user_id])

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: dict):
    username = form_data.get("username")
    password = form_data.get("password")
    
    # Find user
    user = None
    for u in users_db.values():
        if u["username"] == username:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Simple token (in real app, use JWT)
    token = f"demo_token_{user['id']}_{datetime.now().timestamp()}"
    
    return Token(access_token=token)

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user(authorization: str = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")
    
    # Extract user ID from demo token
    token = authorization.replace("Bearer ", "")
    if not token.startswith("demo_token_"):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        user_id = int(token.split("_")[2])
        if user_id not in users_db:
            raise HTTPException(status_code=401, detail="User not found")
        
        return UserResponse(**users_db[user_id])
    except (IndexError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/ux-agent/chat", response_model=UXAgentResponse)
async def chat_with_ux_agent(request: UXAgentRequest):
    # Generate response
    response = get_agent_response(request.message, request.agent_type)
    
    # Create conversation record
    conversation_id = len(conversations_db) + 1
    conversations_db[conversation_id] = {
        "id": conversation_id,
        "title": request.message[:50] + "..." if len(request.message) > 50 else request.message,
        "agent_type": request.agent_type,
        "created_at": datetime.now().isoformat(),
        "messages": [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": response}
        ]
    }
    
    return UXAgentResponse(
        response=response,
        agent_used=request.agent_type,
        knowledge_sources=["UX Knowledge Base"],
        conversation_id=conversation_id
    )

@app.get("/api/ux-agent/conversations", response_model=list[ConversationResponse])
async def get_user_conversations():
    conversations = []
    for conv in conversations_db.values():
        conversations.append(ConversationResponse(**conv))
    
    # Return in reverse chronological order
    return sorted(conversations, key=lambda x: x.created_at, reverse=True)

@app.get("/api/ux-agent/agents")
async def get_available_agents():
    return {
        "agents": {
            "workflow": "UX Workflow Specialist - Process optimization and methodology",
            "thinking": "UX Strategic Thinker - Strategy and user psychology", 
            "writing": "UX Writing Expert - Content and microcopy",
            "triage": "UX Request Triage - Routes requests to appropriate specialists"
        },
        "knowledge_summary": {
            "total_documents": 3,
            "documents": ["Usability testing", "UX workflow in summary", "What is a job story"],
            "types": ["pdf"]
        }
    }

@app.get("/api/payment/pricing")
async def get_pricing():
    return {
        "plans": [
            {
                "id": "basic",
                "name": "Basic Plan",
                "price": 29.99,
                "currency": "usd",
                "interval": "month",
                "features": [
                    "Access to UX Workflow Agent",
                    "Basic UX knowledge base",
                    "5 conversations per month"
                ]
            },
            {
                "id": "premium", 
                "name": "Premium Plan",
                "price": 99.99,
                "currency": "usd",
                "interval": "month",
                "features": [
                    "Access to all UX agents",
                    "Full UX knowledge base", 
                    "Unlimited conversations",
                    "Priority support"
                ]
            }
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting UX AI Agent Simple Backend...")
    print("📱 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
