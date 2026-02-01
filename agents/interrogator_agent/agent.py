"""
Interrogator Agent - Red Team Attacker
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import List, Optional
import random

from shared import LLMClient, get_llm_client, AgentRole, get_logger
from .strategies import (
    get_strategy_prompt,
    get_all_strategies,
    get_strategy_tactics,
    STRATEGIES
)

logger = get_logger(__name__)


class InterrogatorAgent:
    """
    Interrogator Agent that attacks the target agent using various strategies
    to test its robustness, role adherence, and constraint compliance.
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        strategies: List[str],
        temperature: float = 0.8,
        max_tokens: int = 512
    ):
        """
        Initialize Interrogator Agent
        
        Args:
            llm_client: LLM client for generating queries
            strategies: List of attack strategies to use
            temperature: Sampling temperature (higher = more creative)
            max_tokens: Maximum tokens for queries
        """
        self.llm_client = llm_client
        self.strategies = strategies
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.conversation_history: List[dict] = []
        
        # Validate strategies
        valid_strategies = get_all_strategies()
        for strategy in self.strategies:
            if strategy not in valid_strategies:
                raise ValueError(f"Invalid strategy: {strategy}. Valid: {valid_strategies}")
        
        logger.info(f"Interrogator Agent initialized with strategies: {self.strategies}")
    
    def generate_query(
        self,
        target_role: AgentRole,
        turn_number: int,
        previous_responses: Optional[List[str]] = None
    ) -> tuple[str, str]:
        """
        Generate an adversarial query for the target agent
        
        Args:
            target_role: The role the target agent is playing
            turn_number: Current turn number
            previous_responses: Previous target responses (for context)
            
        Returns:
            Tuple of (query, strategy_used)
        """
        # Select strategy for this turn
        strategy = self._select_strategy(turn_number)
        
        # Build context from previous conversation
        conversation_context = self._build_context(previous_responses)
        
        # Get strategy-specific prompt
        system_prompt = get_strategy_prompt(
            strategy=strategy,
            role_description=target_role.description,
            turn_number=turn_number
        )
        
        # Add context about constraints to probe
        if target_role.constraints:
            system_prompt += f"\n\nTARGET CONSTRAINTS TO TEST:\n"
            for constraint in target_role.constraints:
                system_prompt += f"- {constraint}\n"
        
        # Build messages for LLM
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation context if available
        if conversation_context:
            messages.append({
                "role": "user",
                "content": f"Previous conversation context:\n{conversation_context}\n\nGenerate your next query:"
            })
        else:
            messages.append({
                "role": "user",
                "content": "Generate your opening query:"
            })
        
        try:
            # Generate query
            query = self.llm_client.generate(
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Clean up query
            query = query.strip()
            
            # Store in conversation history
            self.conversation_history.append({
                "turn": turn_number,
                "strategy": strategy,
                "query": query
            })
            
            logger.info(f"Turn {turn_number} - Strategy: {strategy}")
            logger.debug(f"Query: {query[:100]}...")
            
            return query, strategy
            
        except Exception as e:
            logger.error(f"Error generating query: {e}")
            # Fallback to simple query
            return f"Can you help me with {target_role.knowledge_domain or 'this matter'}?", strategy
    
    def _select_strategy(self, turn_number: int) -> str:
        """
        Select which strategy to use for this turn
        
        Strategies are selected to ensure variety and progressive difficulty
        """
        if not self.strategies:
            return "role_drift"
        
        # If only one strategy, use it
        if len(self.strategies) == 1:
            return self.strategies[0]
        
        # Rotate through strategies with some randomness
        # Early turns: lighter strategies
        # Later turns: heavier strategies
        
        # Strategy difficulty ordering (roughly)
        difficulty_order = {
            "role_drift": 1,
            "confusion": 2,
            "contradiction": 3,
            "authority_challenge": 4,
            "ethical_probing": 5,
            "emotional_manipulation": 5
        }
        
        # Get available strategies sorted by difficulty
        available = sorted(
            self.strategies,
            key=lambda s: difficulty_order.get(s, 3)
        )
        
        # In early turns (1-3), prefer easier strategies
        if turn_number <= 3:
            candidates = [s for s in available if difficulty_order.get(s, 3) <= 3]
            if not candidates:
                candidates = available[:len(available)//2 + 1]
        # In later turns, use any strategy
        else:
            candidates = available
        
        # Add some randomness
        return random.choice(candidates)
    
    def _build_context(self, previous_responses: Optional[List[str]]) -> str:
        """Build conversation context from previous responses"""
        if not previous_responses:
            return ""
        
        # Include last 2-3 exchanges for context
        recent_turns = self.conversation_history[-3:]
        context_parts = []
        
        for i, turn_data in enumerate(recent_turns):
            if i < len(previous_responses):
                context_parts.append(
                    f"Turn {turn_data['turn']}:\n"
                    f"Interrogator: {turn_data['query']}\n"
                    f"Target: {previous_responses[i]}"
                )
        
        return "\n\n".join(context_parts)
    
    def reset(self):
        """Reset conversation history"""
        self.conversation_history = []
        logger.info("Interrogator Agent reset")


def create_interrogator_agent(
    provider: str = "groq",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    strategies: Optional[List[str]] = None,
    temperature: float = 0.8,
    max_tokens: int = 512
) -> InterrogatorAgent:
    """
    Factory function to create an Interrogator Agent
    
    Args:
        provider: LLM provider
        model: Model name
        api_key: API key (optional)
        strategies: List of strategies to use
        temperature: Sampling temperature
        max_tokens: Maximum tokens
        
    Returns:
        Configured InterrogatorAgent instance
    """
    llm_client = get_llm_client(provider=provider, model=model, api_key=api_key)
    
    if strategies is None:
        strategies = ["role_drift"]
    
    return InterrogatorAgent(
        llm_client=llm_client,
        strategies=strategies,
        temperature=temperature,
        max_tokens=max_tokens
    )