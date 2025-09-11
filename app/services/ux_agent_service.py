"""
UX Agent Service using OpenAI Agents SDK
Creates specialized agents for UX workflow, thinking, and writing
"""

import os
from typing import Dict, Any, List
from agents import Agent, Runner
from app.services.ux_knowledge import UXKnowledgeService
from app.core.config import settings

class UXAgentService:
    """Service for managing UX AI agents"""
    
    def __init__(self):
        self.knowledge_service = UXKnowledgeService()
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize specialized UX agents"""
        
        # UX Workflow Agent
        self.agents["workflow"] = Agent(
            name="UX Workflow Specialist",
            handoff_description="Expert in UX workflow design, process optimization, and methodology",
            instructions="""
            You are a UX Workflow Specialist with deep expertise in:
            - UX design processes and methodologies
            - Workflow optimization for B2B enterprise applications
            - User research and testing methodologies
            - Design thinking and agile UX practices
            - Cross-functional collaboration strategies
            
            Your role is to help B2B enterprises optimize their UX workflows, 
            improve design processes, and implement best practices for user-centered design.
            
            Always provide actionable, enterprise-focused advice with specific steps and methodologies.
            Reference industry standards and proven frameworks when applicable.
            """,
        )
        
        # UX Thinking Agent
        self.agents["thinking"] = Agent(
            name="UX Strategic Thinker",
            handoff_description="Specialist in UX strategy, user psychology, and design thinking",
            instructions="""
            You are a UX Strategic Thinker with expertise in:
            - User psychology and behavior analysis
            - Strategic UX planning and vision
            - Design thinking methodologies
            - User empathy and persona development
            - Business-UX alignment strategies
            
            Your role is to help B2B enterprises develop strategic UX thinking,
            understand user motivations, and align UX initiatives with business goals.
            
            Focus on strategic insights, user psychology, and long-term UX vision.
            Provide frameworks for thinking about users and their needs in enterprise contexts.
            """,
        )
        
        # UX Writing Agent
        self.agents["writing"] = Agent(
            name="UX Writing Expert",
            handoff_description="Specialist in UX writing, content strategy, and microcopy",
            instructions="""
            You are a UX Writing Expert with expertise in:
            - UX writing and microcopy
            - Content strategy for digital products
            - Information architecture and content organization
            - Voice and tone development
            - Accessibility in written content
            
            Your role is to help B2B enterprises create clear, effective, and user-friendly content
            for their digital products and interfaces.
            
            Focus on writing that guides users, reduces cognitive load, and improves user experience.
            Provide specific writing examples and content guidelines.
            """,
        )
        
        # Triage Agent for routing requests
        self.agents["triage"] = Agent(
            name="UX Request Triage",
            instructions="""
            You are a UX Request Triage agent that determines which specialist agent
            should handle a user's request based on the content and intent.
            
            Route requests to:
            - workflow: Process optimization, methodology, workflow design
            - thinking: Strategy, user psychology, design thinking, personas
            - writing: Content, microcopy, information architecture, writing guidelines
            
            Always provide a brief explanation of why you're routing to a specific agent.
            """,
            handoffs=[self.agents["workflow"], self.agents["thinking"], self.agents["writing"]]
        )
    
    async def process_request(self, user_input: str, agent_type: str = "triage") -> Dict[str, Any]:
        """Process a user request using the appropriate agent"""
        try:
            if agent_type not in self.agents:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            # Get relevant knowledge context
            knowledge_context = self._get_knowledge_context(user_input)
            
            # Prepare the input with knowledge context
            enhanced_input = f"""
            User Request: {user_input}
            
            Relevant UX Knowledge Context:
            {knowledge_context}
            
            Please provide a comprehensive response based on the user's request and the provided UX knowledge.
            """
            
            # Run the agent
            result = await Runner.run(self.agents[agent_type], enhanced_input)
            
            return {
                "success": True,
                "response": result.final_output,
                "agent_used": agent_type,
                "knowledge_sources": self._get_used_knowledge_sources(user_input)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_used": agent_type
            }
    
    def _get_knowledge_context(self, user_input: str) -> str:
        """Get relevant knowledge context for the user input"""
        # Search for relevant knowledge
        search_results = self.knowledge_service.search_knowledge(user_input, max_results=3)
        
        if not search_results:
            return "No specific knowledge context found. Rely on general UX expertise."
        
        context_parts = []
        for result in search_results:
            context_parts.append(f"From {result['title']}: {result['preview']}")
        
        return "\n\n".join(context_parts)
    
    def _get_used_knowledge_sources(self, user_input: str) -> List[str]:
        """Get list of knowledge sources used for the response"""
        search_results = self.knowledge_service.search_knowledge(user_input, max_results=3)
        return [result['title'] for result in search_results]
    
    def get_available_agents(self) -> Dict[str, str]:
        """Get list of available agents and their descriptions"""
        return {
            "workflow": "UX Workflow Specialist - Process optimization and methodology",
            "thinking": "UX Strategic Thinker - Strategy and user psychology",
            "writing": "UX Writing Expert - Content and microcopy",
            "triage": "UX Request Triage - Routes requests to appropriate specialists"
        }
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get summary of available knowledge base"""
        return self.knowledge_service.get_knowledge_summary()
