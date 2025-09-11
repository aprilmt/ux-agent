"""
Authentication Schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_premium: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str
