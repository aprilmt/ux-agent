#!/usr/bin/env python3
"""
LLM-powered backend server for UX AI Agent
Uses OpenAI API for intelligent responses
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
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Simple in-memory storage for demo
users_db = {}
conversations_db = {}
current_user_id = 1

app = FastAPI(title="UX AI Agent - LLM Backend", version="1.0.0")

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

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: str

class UXAgentRequest(BaseModel):
    message: str
    agent_type: str = "triage"

class UXAgentResponse(BaseModel):
    response: str
    agent_used: str
    knowledge_sources: list
    conversation_id: int

# Agent configurations
AGENT_CONFIGS = {
    "workflow": {
        "name": "UX Workflow Specialist",
        "system_prompt": """You are a UX Workflow Specialist with deep expertise in:
- UX design processes and methodologies
- Workflow optimization for B2B enterprise applications
- User research and testing methodologies
- Design thinking and agile UX practices
- Cross-functional collaboration strategies

Your role is to help B2B enterprises optimize their UX workflows, 
improve design processes, and implement best practices for user-centered design.

Always provide actionable, enterprise-focused advice with specific steps and methodologies.
Reference industry standards and proven frameworks when applicable.

Format your responses with clear structure and actionable recommendations."""
    },
    "thinking": {
        "name": "UX Strategic Thinker",
        "system_prompt": """You are a UX Strategic Thinker with expertise in:
- User psychology and behavior analysis
- Strategic UX planning and vision
- Design thinking methodologies
- User empathy and persona development
- Business-UX alignment strategies

Your role is to help B2B enterprises develop strategic UX thinking,
understand user motivations, and align UX initiatives with business goals.

Focus on strategic insights, user psychology, and long-term UX vision.
Provide frameworks for thinking about users and their needs in enterprise contexts.

Format your responses with strategic insights and psychological frameworks."""
    },
    "writing": {
        "name": "UX Writing Expert",
        "system_prompt": """You are a UX Writing Expert with expertise in:
- UX writing and microcopy
- Content strategy for digital products
- Information architecture and content organization
- Voice and tone development
- Accessibility in written content

Your role is to help B2B enterprises create clear, effective, and user-friendly content
for their digital products and interfaces.

Focus on writing that guides users, reduces cognitive load, and improves user experience.
Provide specific writing examples and content guidelines.

Format your responses with writing examples and content guidelines."""
    },
    "triage": {
        "name": "UX Request Triage",
        "system_prompt": """You are a UX Request Triage agent that determines which specialist agent
should handle a user's request based on the content and intent.

Route requests to:
- workflow: Process optimization, methodology, workflow design
- thinking: Strategy, user psychology, design thinking, personas
- writing: Content, microcopy, information architecture, writing guidelines

Always provide a brief explanation of why you're routing to a specific agent.

Format your response as:
I've analyzed your request and recommend consulting with our UX specialists. Based on your question, I suggest:
1) For process and workflow questions → UX Workflow Specialist.
2) For strategic and user psychology questions → UX Strategic Thinker.
3) For content and writing questions → UX Writing Expert.

Would you like me to connect you with a specific specialist?"""
    }
}

def get_llm_response(message: str, agent_type: str) -> str:
    """Generate response using OpenAI API"""
    try:
        config = AGENT_CONFIGS.get(agent_type, AGENT_CONFIGS["triage"])
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4o-mini for cost efficiency
            messages=[
                {"role": "system", "content": config["system_prompt"]},
                {"role": "user", "content": message}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Fallback to simple response if API fails
        return f"I apologize, but I'm experiencing technical difficulties. Please try again later. (Error: {str(e)})"

# API Routes
@app.get("/")
async def root():
    return {"message": "UX AI Agent LLM API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "UX AI Agent LLM"}

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
    """Chat with UX AI agent using LLM"""
    # Generate response using LLM
    response = get_llm_response(request.message, request.agent_type)
    
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
        knowledge_sources=["UX Knowledge Base", "OpenAI GPT-4o-mini"],
        conversation_id=conversation_id
    )

@app.post("/api/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
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
        "password": user_data.password,  # In production, hash this
        "created_at": datetime.now().isoformat()
    }
    
    return UserResponse(**users_db[user_id])

@app.post("/api/auth/login")
async def login(login_data: UserLogin):
    """Login user"""
    for user in users_db.values():
        if user["email"] == login_data.email and user["password"] == login_data.password:
            # In production, use JWT tokens
            return {"access_token": f"mock_token_{user['id']}", "token_type": "bearer"}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/user/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(lambda: "mock_token_1")):
    """Get current user info"""
    try:
        user_id = int(token.split("_")[-1])
        return UserResponse(**users_db[user_id])
    except (IndexError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

if __name__ == "__main__":
    print("🚀 Starting UX AI Agent LLM Backend...")
    print("📱 Frontend: http://localhost:8080")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🤖 Using OpenAI GPT-4o-mini for intelligent responses")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
