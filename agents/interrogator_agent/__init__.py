"""
Interrogator Agent Module
"""
from .agent import InterrogatorAgent, create_interrogator_agent
from .strategies import (
    STRATEGIES,
    get_all_strategies,
    get_strategy_description,
    get_strategy_tactics,
    get_strategy_templates,
    get_strategy_prompt
)

__all__ = [
    "InterrogatorAgent",
    "create_interrogator_agent",
    "STRATEGIES",
    "get_all_strategies",
    "get_strategy_description",
    "get_strategy_tactics",
    "get_strategy_templates",
    "get_strategy_prompt"
]