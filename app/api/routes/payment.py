"""
Payment Routes for Stripe Integration
"""

import stripe
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.models.payment import Payment
from app.schemas.payment import PaymentIntentCreate, PaymentIntentResponse

router = APIRouter()

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@router.post("/create-payment-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe payment intent for subscription"""
    
    try:
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=payment_data.amount,  # Amount in cents
            currency=payment_data.currency,
            metadata={
                "user_id": str(current_user.id),
                "subscription_type": payment_data.subscription_type
            }
        )
        
        # Save payment record
        payment = Payment(
            user_id=current_user.id,
            stripe_payment_intent_id=intent.id,
            amount=payment_data.amount / 100,  # Convert from cents
            currency=payment_data.currency,
            status="pending"
        )
        
        db.add(payment)
        db.commit()
        
        return PaymentIntentResponse(
            client_secret=intent.client_secret,
            payment_intent_id=intent.id
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating payment intent: {str(e)}"
        )

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        
        # Update payment status
        payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent["id"]
        ).first()
        
        if payment:
            payment.status = "succeeded"
            
            # Update user premium status
            user = db.query(User).filter(User.id == payment.user_id).first()
            if user:
                user.is_premium = True
                user.subscription_id = payment_intent.get("id")
            
            db.commit()
    
    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        
        # Update payment status
        payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent["id"]
        ).first()
        
        if payment:
            payment.status = "failed"
            db.commit()
    
    return {"status": "success"}

@router.get("/pricing")
async def get_pricing():
    """Get subscription pricing information"""
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
                    "Priority support",
                    "Advanced analytics"
                ]
            }
        ]
    }
