"""
User Schemas
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    """User schema"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_premium: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    full_name: Optional[str] = None
    email: Optional[str] = None
