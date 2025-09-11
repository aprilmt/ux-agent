"""
Payment Schemas
"""

from pydantic import BaseModel
from typing import Optional

class PaymentIntentCreate(BaseModel):
    """Schema for creating payment intent"""
    amount: int  # Amount in cents
    currency: str = "usd"
    subscription_type: str

class PaymentIntentResponse(BaseModel):
    """Schema for payment intent response"""
    client_secret: str
    payment_intent_id: str
