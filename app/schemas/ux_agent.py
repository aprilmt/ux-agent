"""
UX Agent Schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class UXAgentRequest(BaseModel):
    """Schema for UX agent requests"""
    message: str
    agent_type: Optional[str] = "triage"  # workflow, thinking, writing, triage
    conversation_id: Optional[int] = None

class UXAgentResponse(BaseModel):
    """Schema for UX agent responses"""
    response: str
    agent_used: str
    knowledge_sources: List[str]
    conversation_id: int

class ConversationCreate(BaseModel):
    """Schema for creating a conversation"""
    title: str
    agent_type: str

class ConversationResponse(BaseModel):
    """Schema for conversation responses"""
    id: int
    title: str
    agent_type: str
    created_at: datetime
    messages: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        from_attributes = True
