#!/usr/bin/env python3
"""
Ollama-powered backend for UX AI Agent
Uses local Ollama service for LLM responses
"""

import os
import json
import asyncio
import httpx
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="UX AI Agent - Ollama Backend", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

# Root route - serve the UX agent HTML file
@app.get("/")
async def read_root():
    return FileResponse("ux-agent.html")

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")

# Pydantic models
class UXAgentRequest(BaseModel):
    message: str
    agent_type: str = "triage"
    conversation_id: Optional[int] = None

class UXAgentResponse(BaseModel):
    response: str
    agent_used: str
    knowledge_sources: list
    conversation_id: int
    chat_history: list = []

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: str

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

## Core UX Workflow Knowledge:

### Problem Statements
A problem statement clearly defines the issue a design aims to address. It should be concise, comprehensive, actionable, and measurable, while aligning with both user needs and business goals. A complete problem statement should include:
- Title or Problem Summary: A concise, descriptive title
- Context/Background: A brief description of the environment or situation
- Problem Description: A clear articulation of the problem
- Impact: Highlights the negative effects of the problem
- Evidence: Provides supporting data, user feedback, or observations
- Goal/Objective: States what success will look like once the problem is solved, often using measurable metrics

### B2B UX Team Processes and Tools
- Jira: Required tool for documenting design assets, requirements, and design implementation framework
- Google Docs (Slides): Used during discovery phase to gather and communicate key insights from research and analytics
- Miro: Collaborative tool for discovery phase, used to involve stakeholders, document user flows, and outline questions
- Figma: Projects organized with specific folder structure, including main folder for project and subfolders for specific projects
- Product-specific Component Library: Centralizes components from the design system library

### Research and Documentation
Three primary avenues for gathering customer insights:
- Continuous Interviews: Ongoing, frequent conversations providing up-to-date user feedback
- Standalone Research Studies: One-off projects allowing for larger sample sizes and wider range of research methods
- Telemetry: Continuous collection of data from users' interactions with the product, providing large amount of data on user behavior but lacks context

All research data is documented in EnjoyHQ, the primary data repository. Each project gets a dedicated folder including study plan, data (like recordings or notes), a report, and "stories" that link related findings.

### User Flow Mapping
User flows are step-by-step visual mapping processes outlining all potential actions a user would take on a website or app when moving from an entry point toward a successful outcome. They help:
- Create intuitive interfaces by understanding specific actions users are trying to take
- Evaluate existing interfaces and point out pain points
- Present design ideas to stakeholders in a tangible, easy-to-read format
- Support designers in different stages of the Design Process, especially during Discovery phase

### Product Analytics
Product analytics is a method used to collect, measure, and analyze user data within a digital product or service. It involves utilizing various tools and technologies to gather quantitative and qualitative information about user interactions, behaviors, and preferences. This method aids in understanding how users engage with a product, identifying areas for improvement, and making data-driven decisions to enhance the overall user experience.

Key steps for product analytics:
1. Define goals and metrics: Establish clear objectives for data collection and determine KPIs aligned with UX goals
2. Select tools and set up analytics: Choose appropriate analytics tools and implement tracking codes
3. Collect and analyze data: Continuously collect user data and perform regular analyses
4. Iterate and improve: Implement changes based on insights gained from analytics

Your role is to help B2B enterprises optimize their UX workflows, improve design processes, and implement best practices for user-centered design.

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

## Core Strategic UX Knowledge:

### Job Stories Framework
Job stories help define user tasks in product design. They are a more generalized version of user stories, with a focus on explaining the triggering situation or context of the task, rather than revolving around who is taking the task (the persona).

**Job Story Template:**
"When [situation], I want to [motivation], so I can [outcome]."

**Job Story Development Process:**
Start with a broad and generic story, then add details little-by-little to turn it into a more specific and focused job story. This iterative approach helps refine the understanding of user needs and context.

**Example Progression for Help-Seeking User:**
1. **Broad/Generic:** "When I need help, I want to find information, so I can solve my problem."
2. **More Specific:** "When I'm stuck on a new platform, I want to find help resources, so I can continue using the tool effectively."
3. **Focused:** "When I encounter an error message I don't understand on a new platform, I want to quickly access contextual help, so I can resolve the issue without losing my work progress."

**Why Job Stories Matter:**
- They describe the what and the why by describing motivation and context
- They allow the team to focus on the how by not prescribing any particular implementation
- They make the user's pain points easily visible and help the team consider problems from every angle
- They prepare the ground for further validation of the cause-effect relationship through methods like user interviews or usability testing
- The iterative refinement process helps uncover deeper user needs and context

**Job Story vs User Story:**
- User Story: "As a [persona], I want to [action], so I can [outcome]"
- Job Story: "When [situation], I want to [motivation], so I can [outcome]"
- A user story provides a persona; A job story provides context
- Personas are hypothetical and don't represent actual users, while job stories focus on causality and context

**When to Use Job Stories:**
- During Discovery phase of the design process (pre- and post-user-research)
- Before user research to get alignment across the team on what user needs and outcomes need to be validated
- When refining user requirements through iterative story development
- After user research to turn user insights into actionable prompts for designers
- Throughout the product development process to drive conversation between stakeholders

**How to Write Effective Job Stories:**
1. Be specific, focus on user needs, and articulate clear motivations and outcomes
2. Start broad and add details little by little
3. Ask basic questions like when and why when provided with vague requirements
4. Branch into multiple job stories when you end up with multiple valid options
5. Consider adding persona details if your team relies heavily on them

### User Psychology and Behavior Analysis
Understanding user motivations, contexts, and behaviors is crucial for creating effective UX strategies. Focus on:
- The causal relationship between user situations and their needs
- Context that drives user behavior and decision-making
- Pain points and opportunities for improvement
- User mental models and expectations

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

## Core UX Writing Knowledge:

### Usability Testing for Content
Usability testing is a method for evaluating a product or service to ensure that it is usable for the target audience. During a usability test, participants complete tasks with a prototype or live software while a facilitator observes, asks questions, and takes notes.

**When to Use Usability Testing:**
- Test an existing product or a new design
- Test interactions, wording, and design elements to make sure they are user-friendly
- Identify confusion or issues
- Understand the actual behavior and preferences of users
- Discover opportunities to improve
- Benchmark task performance for future comparison

**Key Usability Testing Principles:**
- You don't need fully functional software to perform a usability test
- You can test really rough concepts, even things you've sketched on paper
- Low-fidelity software prototypes can be created using design tools like Sketch or Figma
- Usability testing should not generally be used as a discovery method or to collect quantitative data from a large sample of people

**Usability Test Script Structure:**
1. General introduction
2. Background questions
3. Tasks for testing
4. Summary questions

**Task Design Best Practices:**
- Write tasks to be goal-oriented and give participants instructions about what they should accomplish, not how to do it
- Place tasks in a realistic sequence when possible
- Limit the number of tasks to 8 or less so participants don't feel overwhelmed
- Start by asking for first impressions before they attempt to complete the first task

**Moderation Guidelines:**
- Remind participants to think out loud
- Have the participant read back the task
- Allow them to say when they think they're done
- Let them struggle a bit and ask probing questions
- Ask open-ended questions and avoid leading questions
- Embrace awkward silence and let them talk

**Content-Specific Testing Focus:**
- Test terminology and labeling clarity
- Evaluate content hierarchy and information architecture
- Assess microcopy effectiveness (buttons, error messages, help text)
- Test content accessibility and readability
- Validate content against user mental models

Your role is to help B2B enterprises create clear, effective, and user-friendly content
for their digital products and interfaces.

Focus on writing that guides users, reduces cognitive load, and improves user experience.
Provide specific writing examples and content guidelines.

Format your responses with writing examples and content guidelines."""
    },
    "triage": {
        "name": "UX Request Triage",
        "system_prompt": """You are a UX Request Triage agent that provides direct, helpful answers to UX questions. Only route to specialists for very complex or highly specialized topics that require deep expertise.

**Primary Goal**: Answer the user's question directly with practical, actionable advice. Be specific and helpful rather than generic.

## Core UX Knowledge Base:

### Problem Statements
A problem statement clearly defines the issue a design aims to address. It should be concise, comprehensive, actionable, and measurable, while aligning with both user needs and business goals. Include: Title/Summary, Context/Background, Problem Description, Impact, Evidence, and Goal/Objective.

### User Flows
User flows are step-by-step visual mapping processes outlining all potential actions a user would take on a website or app when moving from an entry point toward a successful outcome. They help create intuitive interfaces, evaluate existing interfaces, and present design ideas to stakeholders.

### Job Stories
Job stories help define user tasks in product design using the format: "When [situation], I want to [motivation], so I can [outcome]." They focus on context and causality rather than personas, making user pain points visible and preparing for validation through user research.

### Usability Testing
A method for evaluating a product or service to ensure it's usable for the target audience. Participants complete tasks while a facilitator observes and takes notes. Key principles: test early and often, focus on goal-oriented tasks, use open-ended questions, and embrace user struggles to understand their mental models.

### Product Analytics
A method to collect, measure, and analyze user data within digital products. Key steps: define goals and metrics, select appropriate tools, collect and analyze data continuously, and iterate based on insights to enhance user experience.

### B2B UX Tools and Processes
- Jira: Document design assets and requirements
- Miro: Collaborative discovery and user flow mapping
- Figma: Design with organized folder structures
- Google Docs: Communicate research insights
- EnjoyHQ: Primary research data repository

You can directly answer questions about:
- Basic UX concepts and definitions
- General UX strategy and planning
- Common UX processes and methodologies
- General UX best practices
- Problem statement creation
- User flow mapping basics
- Job story writing (with iterative refinement process)
- Usability testing fundamentals
- Product analytics overview

### Job Story Writing Framework
When helping with job stories, use this iterative approach:

**Template:** "When [situation], I want to [motivation], so I can [outcome]."

**Development Process:** Start with a broad and generic story, then add details little-by-little to turn it into a more specific and focused job story.

**Example Progression for Help-Seeking User:**
1. **Broad/Generic:** "When I need help, I want to find information, so I can solve my problem."
2. **More Specific:** "When I'm stuck on a new platform, I want to find help resources, so I can continue using the tool effectively."
3. **Focused:** "When I encounter an error message I don't understand on a new platform, I want to quickly access contextual help, so I can resolve the issue without losing my work progress."

Always guide users through this iterative refinement process when creating job stories.

### UX Strategy Alignment
When users ask about aligning UX strategy with business goals:
1. **Identify Business Objectives**: Revenue, user acquisition, retention, efficiency
2. **Map UX Metrics**: User satisfaction, task completion, engagement, conversion
3. **Create Alignment Framework**: Connect UX activities to business outcomes
4. **Establish Success Metrics**: Define measurable UX KPIs that impact business goals
5. **Regular Review Process**: Set up quarterly reviews to ensure continued alignment

### UX Strategy Roadmap Creation
When users ask about creating UX strategy roadmaps:
1. **Current State Assessment**: Audit existing UX maturity and capabilities
2. **Stakeholder Alignment**: Get buy-in from business, product, and engineering teams
3. **Define UX Vision**: Create a clear, inspiring vision for user experience
4. **Prioritize Initiatives**: Rank UX activities by impact and feasibility
5. **Timeline Planning**: Create realistic phases with clear milestones
6. **Resource Planning**: Identify team needs, tools, and budget requirements
7. **Success Metrics**: Define how you'll measure progress and impact

**Always provide specific, actionable steps rather than generic routing advice.**

Route complex requests to specialists:
- workflow: Detailed process optimization, specific methodologies, workflow design, B2B team processes, research documentation
- thinking: Advanced strategy, user psychology, design thinking, job story frameworks, user behavior analysis
- writing: Content strategy, microcopy, information architecture, writing guidelines, usability testing for content

When a user asks follow-up questions or for more details, provide additional helpful information rather than just repeating recommendations.

Be conversational, helpful, and context-aware. If you've already recommended a specialist, don't repeat the same recommendation unless the user specifically asks for it."""
    }
}

# Enhanced mock responses for fallback (when Ollama is not available)
MOCK_RESPONSES = {
    "workflow": """I'm your UX Workflow Specialist! I can help you optimize design processes, implement user research methodologies, and improve cross-functional collaboration.

**Key Areas I Help With:**
- Design process optimization
- User research methodologies
- Cross-functional collaboration
- Workflow efficiency improvements
- Tool and framework recommendations

What specific workflow challenge are you facing? I'll provide practical, actionable advice to help you streamline your UX processes.""",
    
    "thinking": """I'm your UX Strategic Thinker! I specialize in user psychology, strategic planning, and aligning UX with business goals.

**Key Areas I Help With:**
- User psychology and behavior analysis
- Strategic UX planning
- Business goal alignment
- User research strategy
- Design thinking methodologies

How can I help you develop a deeper understanding of your users and create more strategic UX approaches?""",
    
    "writing": """I'm your UX Writing Expert! I help create clear, effective content and microcopy that guides users and improves their experience.

**Key Areas I Help With:**
- Microcopy and interface text
- Content strategy
- User guidance and instructions
- Error messages and feedback
- Voice and tone development

What writing challenge can I help you with? I'll provide specific, actionable advice for creating user-centered content.""",
    
    "triage": """I'm here to help with your UX questions! I can provide direct, actionable advice on a wide range of UX topics.

**I can help you with:**
- **Job Story Writing**: Use our iterative refinement process to create focused user stories
- **UX Strategy Alignment**: Connect UX activities with business goals
- **UX Strategy Roadmaps**: Plan and prioritize UX initiatives
- **User Research Methods**: Choose the right research approach for your context
- **Workflow Optimization**: Improve your design processes
- **Content Strategy**: Create effective user-centered content

**Job Story Framework:**
When [situation], I want to [motivation], so I can [outcome].

Start broad and generic, then add details little-by-little to create focused, specific job stories.

What specific UX challenge can I help you with today?"""
}

def check_ollama_available() -> bool:
    """Check if Ollama service is available"""
    try:
        print(f"🔍 Checking Ollama at {OLLAMA_BASE_URL}/api/tags")
        import httpx
        # Disable proxy to avoid Privoxy interference
        with httpx.Client(trust_env=False) as client:
            response = client.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5.0)
            print(f"📡 Ollama response status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Ollama service is available!")
                return True
            else:
                print(f"❌ Ollama returned status {response.status_code}")
                print(f"Response text: {response.text[:200]}")
                return False
    except Exception as e:
        print(f"❌ Ollama not available: {e}")
        return False

def get_ollama_response_sync(message: str, agent_type: str, conversation_id: int) -> str:
    """Generate response using Ollama API (synchronous)"""
    try:
        # Build prompt with chat history context
        prompt = build_context_prompt(agent_type, message, conversation_id)
        
        # Call Ollama API
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500  # 使用num_predict而不是max_tokens
                }
            },
            timeout=60.0  # Standard timeout for Mistral model
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "No response generated")
        else:
            print(f"❌ Ollama API error: {response.status_code} - {response.text}")
            return f"Ollama API error: {response.status_code}"
            
    except Exception as e:
        print(f"❌ Ollama request error: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return f"Ollama service error: {str(e)}"

def get_smart_fallback_response(message: str, agent_type: str) -> str:
    """Generate intelligent fallback response based on user question"""
    message_lower = message.lower()
    
    # Job story related questions
    if any(keyword in message_lower for keyword in ["job story", "user story", "story writing"]):
        return """**Job Story Writing Guide**

I'll help you create effective job stories using our iterative refinement process.

**Template:** "When [situation], I want to [motivation], so I can [outcome]."

**Development Process:**
1. **Start Broad**: "When I need help, I want to find information, so I can solve my problem."
2. **Add Context**: "When I'm stuck on a new platform, I want to find help resources, so I can continue using the tool effectively."
3. **Get Specific**: "When I encounter an error message I don't understand on a new platform, I want to quickly access contextual help, so I can resolve the issue without losing my work progress."

**Key Benefits:**
- Focuses on user context and motivation
- More flexible than user stories
- Helps identify real user needs
- Guides design decisions

What specific user situation are you trying to capture in a job story?"""

    # UX strategy alignment questions
    elif any(keyword in message_lower for keyword in ["align", "strategy", "business goals", "roadmap"]):
        return """**UX Strategy Alignment Framework**

Here's how to connect your UX work with business objectives:

**1. Identify Business Objectives**
- Revenue growth
- User acquisition
- Customer retention
- Operational efficiency
- Market expansion

**2. Map UX Metrics to Business Goals**
- User satisfaction → Customer retention
- Task completion → Operational efficiency
- User engagement → Revenue growth
- Conversion rates → User acquisition

**3. Create Alignment Framework**
- Define UX KPIs that impact business metrics
- Establish regular review processes
- Set up cross-functional collaboration
- Measure and iterate

**4. UX Strategy Roadmap Creation**
- Current state assessment
- Stakeholder alignment
- Define UX vision
- Prioritize initiatives by impact/feasibility
- Timeline and resource planning

What specific aspect of UX strategy alignment would you like to focus on?"""

    # User research questions
    elif any(keyword in message_lower for keyword in ["user research", "research methods", "b2b research"]):
        return """**User Research Methods for B2B Contexts**

**Effective B2B Research Approaches:**

**1. Stakeholder Interviews**
- Interview decision-makers and end-users
- Understand business processes and pain points
- Map user journeys across different roles

**2. Contextual Inquiry**
- Observe users in their work environment
- Understand real-world constraints and workflows
- Identify unmet needs and opportunities

**3. Surveys and Analytics**
- Quantitative data on user behavior
- Usage patterns and feature adoption
- Satisfaction and NPS scores

**4. Usability Testing**
- Task-based testing with realistic scenarios
- A/B testing for feature improvements
- Accessibility testing

**5. Competitive Analysis**
- Study similar B2B products
- Identify best practices and gaps
- Benchmark user experience

What specific research challenge are you facing?"""

    # Default to enhanced triage response
    else:
        return MOCK_RESPONSES.get(agent_type, MOCK_RESPONSES["triage"])

def get_llm_response(message: str, agent_type: str) -> str:
    """Generate response using Ollama or fallback to mock"""
    try:
        # Try to get response from Ollama using asyncio.run()
        response = asyncio.run(get_ollama_response(message, agent_type))
        
        # If response contains error, fallback to smart mock
        if "error" in response.lower() and ("ollama" in response.lower() or "api" in response.lower()):
            print(f"🔄 Falling back to smart mock response due to error: {response[:100]}")
            return get_smart_fallback_response(message, agent_type)
        
        print(f"✅ Using Ollama response: {response[:100]}...")
        return response
        
    except Exception as e:
        print(f"❌ Error getting LLM response: {e}")
        return get_smart_fallback_response(message, agent_type)

# Check Ollama availability on startup
ollama_available = False

# Chat history storage (in production, use a database)
chat_sessions = {}
next_conversation_id = 1

def get_or_create_conversation(conversation_id: int = None) -> int:
    """Get existing conversation or create new one"""
    global next_conversation_id
    if conversation_id is None or conversation_id not in chat_sessions:
        conversation_id = next_conversation_id
        next_conversation_id += 1
        chat_sessions[conversation_id] = []
    return conversation_id

def add_message_to_history(conversation_id: int, role: str, content: str):
    """Add message to chat history"""
    from datetime import datetime
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    chat_sessions[conversation_id].append(message)
    # Keep only last 20 messages to prevent memory issues
    if len(chat_sessions[conversation_id]) > 20:
        chat_sessions[conversation_id] = chat_sessions[conversation_id][-20:]

def build_context_prompt(agent_type: str, message: str, conversation_id: int) -> str:
    """Build prompt with chat history context"""
    config = AGENT_CONFIGS.get(agent_type, AGENT_CONFIGS["triage"])
    base_prompt = config['system_prompt']
    
    # Add recent chat history for context
    history = chat_sessions.get(conversation_id, [])
    if history:
        context = "\n\nRecent conversation history:\n"
        for msg in history[-4:]:  # Last 4 messages for context
            context += f"{msg['role'].title()}: {msg['content']}\n"
        base_prompt += context
        
        # Add context-aware instructions
        base_prompt += "\n\nImportant instructions:"
        base_prompt += "\n- If the user is asking for more details or clarification, provide additional helpful information"
        base_prompt += "\n- If the user is asking follow-up questions, answer them directly based on the conversation context"
        base_prompt += "\n- Do not repeat previous recommendations unless specifically asked"
        base_prompt += "\n- Be conversational and build on the previous conversation"
        base_prompt += "\n- If you've already recommended a specialist, focus on answering the user's current question"
    
    base_prompt += f"\n\nUser: {message}\n\nAssistant:"
    return base_prompt

@app.on_event("startup")
async def startup_event():
    global ollama_available
    ollama_available = check_ollama_available()
    if ollama_available:
        print(f"✅ Ollama service available with model: {OLLAMA_MODEL}")
    else:
        print("⚠️  Ollama service not available, using mock responses")

# API Routes
@app.get("/")
async def root():
    return {
        "message": "UX AI Agent Ollama API", 
        "status": "running",
        "ollama_available": ollama_available,
        "ollama_model": OLLAMA_MODEL if ollama_available else None,
        "llm_type": f"Ollama {OLLAMA_MODEL}" if ollama_available else "Mock Responses"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "UX AI Agent Ollama",
        "ollama_available": ollama_available,
        "ollama_model": OLLAMA_MODEL if ollama_available else None,
        "llm_type": f"Ollama {OLLAMA_MODEL}" if ollama_available else "Mock Responses"
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

@app.get("/api/ux-agent/chat-history/{conversation_id}")
async def get_chat_history(conversation_id: int):
    """Get chat history for a conversation"""
    if conversation_id in chat_sessions:
        return {
            "conversation_id": conversation_id,
            "messages": chat_sessions[conversation_id]
        }
    else:
        return {
            "conversation_id": conversation_id,
            "messages": []
        }

@app.delete("/api/ux-agent/chat-history/{conversation_id}")
async def clear_chat_history(conversation_id: int):
    """Clear chat history for a conversation"""
    if conversation_id in chat_sessions:
        chat_sessions[conversation_id] = []
        return {"message": f"Chat history cleared for conversation {conversation_id}"}
    else:
        return {"message": f"Conversation {conversation_id} not found"}

@app.post("/api/ux-agent/chat", response_model=UXAgentResponse)
async def chat_with_ux_agent(request: UXAgentRequest):
    """Chat with UX AI agent using Ollama with chat history"""
    # Get or create conversation
    conversation_id = get_or_create_conversation(request.conversation_id)
    
    # Add user message to history
    add_message_to_history(conversation_id, "user", request.message)
    
    # Generate response using LLM
    if ollama_available:
        response = get_ollama_response_sync(request.message, request.agent_type, conversation_id)
        # If response contains error, fallback to smart mock
        if "error" in response.lower() and ("ollama" in response.lower() or "api" in response.lower()):
            print(f"🔄 Falling back to smart mock response due to error: {response[:100]}")
            response = get_smart_fallback_response(request.message, request.agent_type)
        else:
            print(f"✅ Using Ollama response: {response[:100]}...")
    else:
        response = get_smart_fallback_response(request.message, request.agent_type)
    
    # Add assistant response to history
    add_message_to_history(conversation_id, "assistant", response)
    
    return UXAgentResponse(
        response=response,
        agent_used=request.agent_type,
        knowledge_sources=["UX Knowledge Base", f"Ollama {OLLAMA_MODEL}" if ollama_available else "Mock LLM"],
        conversation_id=conversation_id,
        chat_history=chat_sessions[conversation_id]
    )

if __name__ == "__main__":
    print("🚀 Starting UX AI Agent Ollama Backend...")
    print("📱 Frontend: http://localhost:8080")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print(f"🤖 Using Ollama service with model: {OLLAMA_MODEL}")
    print("💡 Make sure Ollama is running: ollama serve")
    print("💡 Install model: ollama pull llama3.2")
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
