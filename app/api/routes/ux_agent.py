"""
UX Agent Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.conversation import Conversation
from app.schemas.ux_agent import UXAgentRequest, UXAgentResponse, ConversationCreate, ConversationResponse
from app.services.ux_agent_service import UXAgentService

router = APIRouter()

# Initialize UX Agent Service
ux_agent_service = UXAgentService()

@router.post("/chat", response_model=UXAgentResponse)
async def chat_with_ux_agent(
    request: UXAgentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Chat with the UX AI agent"""
    
    # Check if user has premium access
    if not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required to access UX AI agent"
        )
    
    try:
        # Process the request with the UX agent
        result = await ux_agent_service.process_request(
            user_input=request.message,
            agent_type=request.agent_type or "triage"
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Agent processing failed: {result['error']}"
            )
        
        # Save conversation to database
        conversation = Conversation(
            user_id=current_user.id,
            title=request.message[:50] + "..." if len(request.message) > 50 else request.message,
            agent_type=result["agent_used"],
            messages=[
                {"role": "user", "content": request.message},
                {"role": "assistant", "content": result["response"]}
            ]
        )
        
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        return UXAgentResponse(
            response=result["response"],
            agent_used=result["agent_used"],
            knowledge_sources=result["knowledge_sources"],
            conversation_id=conversation.id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )

@router.get("/agents")
async def get_available_agents():
    """Get list of available UX agents"""
    return {
        "agents": ux_agent_service.get_available_agents(),
        "knowledge_summary": ux_agent_service.get_knowledge_summary()
    }

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation"""
    
    conversation = Conversation(
        user_id=current_user.id,
        title=conversation_data.title,
        agent_type=conversation_data.agent_type,
        messages=[]
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        agent_type=conversation.agent_type,
        created_at=conversation.created_at
    )

@router.get("/conversations", response_model=list[ConversationResponse])
async def get_user_conversations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's conversations"""
    
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()
    
    return [
        ConversationResponse(
            id=conv.id,
            title=conv.title,
            agent_type=conv.agent_type,
            created_at=conv.created_at
        )
        for conv in conversations
    ]

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation"""
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        agent_type=conversation.agent_type,
        created_at=conversation.created_at,
        messages=conversation.messages
    )
