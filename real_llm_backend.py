#!/usr/bin/env python3
"""
Real LLM-powered backend for UX AI Agent
Uses OpenAI API with proper error handling
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Try to import OpenAI, fallback to mock if not available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI not available, using mock responses")

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    ENV_LOADED = True
except ImportError:
    ENV_LOADED = False
    print("⚠️  python-dotenv not available, using system environment")

app = FastAPI(title="UX AI Agent - Real LLM Backend", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client if available
if OPENAI_AVAILABLE:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_openai_api_key_here":
        try:
            client = OpenAI(api_key=api_key)
            print("✅ OpenAI client initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize OpenAI client: {e}")
            OPENAI_AVAILABLE = False
    else:
        print("⚠️  No valid OpenAI API key found")
        OPENAI_AVAILABLE = False

# Pydantic models
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

# Mock responses for fallback
MOCK_RESPONSES = {
    "workflow": "I'm your UX Workflow Specialist! I can help you optimize design processes, implement user research methodologies, and improve cross-functional collaboration. What specific workflow challenge are you facing?",
    "thinking": "I'm your UX Strategic Thinker! I specialize in user psychology, strategic planning, and aligning UX with business goals. How can I help you develop a deeper understanding of your users?",
    "writing": "I'm your UX Writing Expert! I help create clear, effective content and microcopy that guides users and improves their experience. What writing challenge can I help you with?",
    "triage": "I've analyzed your request and recommend consulting with our UX specialists. Based on your question, I suggest:\n1) For process and workflow questions → UX Workflow Specialist.\n2) For strategic and user psychology questions → UX Strategic Thinker.\n3) For content and writing questions → UX Writing Expert.\n\nWould you like me to connect you with a specific specialist?"
}

def get_llm_response(message: str, agent_type: str) -> str:
    """Generate response using OpenAI API or fallback to mock"""
    if OPENAI_AVAILABLE and client:
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
            print(f"❌ OpenAI API error: {e}")
            return f"I apologize, but I'm experiencing technical difficulties with the AI service. Please try again later. (Error: {str(e)})"
    else:
        # Fallback to mock response
        return MOCK_RESPONSES.get(agent_type, MOCK_RESPONSES["triage"])

# API Routes
@app.get("/")
async def root():
    return {
        "message": "UX AI Agent Real LLM API", 
        "status": "running",
        "openai_available": OPENAI_AVAILABLE,
        "llm_type": "OpenAI GPT-4o-mini" if OPENAI_AVAILABLE else "Mock Responses"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "UX AI Agent Real LLM",
        "openai_available": OPENAI_AVAILABLE,
        "llm_type": "OpenAI GPT-4o-mini" if OPENAI_AVAILABLE else "Mock Responses"
    }

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
    """Chat with UX AI agent using real LLM"""
    # Generate response using LLM
    response = get_llm_response(request.message, request.agent_type)
    
    # Create conversation record
    conversation_id = 1  # Simple ID for demo
    
    return UXAgentResponse(
        response=response,
        agent_used=request.agent_type,
        knowledge_sources=["UX Knowledge Base", "OpenAI GPT-4o-mini" if OPENAI_AVAILABLE else "Mock LLM"],
        conversation_id=conversation_id
    )

if __name__ == "__main__":
    print("🚀 Starting UX AI Agent Real LLM Backend...")
    print("📱 Frontend: http://localhost:8080")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    
    if OPENAI_AVAILABLE:
        print("🤖 Using OpenAI GPT-4o-mini for intelligent responses")
    else:
        print("⚠️  Using Mock responses (OpenAI not available)")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
