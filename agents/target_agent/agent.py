"""
Target Agent - Role-Playing Language Agent under evaluation
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import List, Optional, Dict
from shared import LLMClient, get_llm_client, AgentRole, Message, get_logger
from .prompts import build_target_agent_system_prompt, build_context_aware_prompt

logger = get_logger(__name__)


class TargetAgent:
    """
    Target Agent that maintains a specific role while being interrogated.
    This is the agent under evaluation.
    """
    
    def __init__(
        self,
        role: AgentRole,
        llm_client: LLMClient,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        use_context: bool = True
    ):
        """
        Initialize Target Agent
        
        Args:
            role: Agent role definition
            llm_client: LLM client for generating responses
            temperature: Sampling temperature
            max_tokens: Maximum tokens for responses
            use_context: Whether to include conversation context
        """
        self.role = role
        self.llm_client = llm_client
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.use_context = use_context
        
        # Build base system prompt
        self.system_prompt = build_target_agent_system_prompt(
            role_name=role.name,
            role_description=role.description,
            persona=role.persona,
            constraints=role.constraints,
            knowledge_domain=role.knowledge_domain
        )
        
        # Conversation memory
        self.conversation_history: List[Dict] = []
        
        logger.info(f"Target Agent initialized as: {role.name}")
    
    def respond(self, query: str) -> str:
        """
        Generate response to a query while maintaining role
        
        Args:
            query: Interrogator's query
            
        Returns:
            Agent's response
        """
        try:
            # Build messages for LLM
            messages = self._build_messages(query)
            
            # Generate response
            response = self.llm_client.generate(
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Store in conversation history
            self.conversation_history.append({
                "query": query,
                "response": response
            })
            
            logger.debug(f"Query: {query[:50]}...")
            logger.debug(f"Response: {response[:50]}...")
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Fallback response
            return f"I apologize, but I'm having trouble processing that request. As a {self.role.name}, I'm here to help with {self.role.knowledge_domain or 'appropriate matters'}."
    
    def _build_messages(self, query: str) -> List[Dict[str, str]]:
        """Build message list for LLM"""
        messages = [{"role": "system", "content": self.system_prompt}]

        # Replay conversation history as proper chat turns
        if self.use_context and self.conversation_history:
            for turn in self.conversation_history:
                messages.append({"role": "user", "content": turn["query"]})
                messages.append({"role": "assistant", "content": turn["response"]})

        # Add current query
        messages.append({"role": "user", "content": query})

        return messages
    
    def get_role_summary(self) -> Dict:
        """Get summary of agent's role"""
        return {
            "name": self.role.name,
            "description": self.role.description,
            "persona": self.role.persona,
            "constraints": self.role.constraints,
            "knowledge_domain": self.role.knowledge_domain
        }
    
    def reset(self):
        """Reset conversation history"""
        self.conversation_history = []
        logger.info("Target Agent reset")


def create_target_agent(
    role: AgentRole,
    provider: str = "groq",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    use_context: bool = True
) -> TargetAgent:
    """
    Factory function to create a Target Agent
    
    Args:
        role: Agent role definition
        provider: LLM provider
        model: Model name
        api_key: API key (optional)
        temperature: Sampling temperature
        max_tokens: Maximum tokens
        use_context: Whether to use conversation context
        
    Returns:
        Configured TargetAgent instance
    """
    llm_client = get_llm_client(provider=provider, model=model, api_key=api_key)
    
    return TargetAgent(
        role=role,
        llm_client=llm_client,
        temperature=temperature,
        max_tokens=max_tokens,
        use_context=use_context
    )