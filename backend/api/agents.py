"""
API routes for agent information
"""
from fastapi import APIRouter
from typing import List, Dict

from agents.interrogator_agent import get_all_strategies, get_strategy_description, STRATEGIES
from shared import AttackStrategy

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/strategies", response_model=List[Dict])
async def get_strategies():
    """
    Get all available attack strategies
    
    Returns:
        List of strategies with descriptions
    """
    strategies = []
    
    for strategy_key in get_all_strategies():
        strategy_info = STRATEGIES.get(strategy_key, {})
        strategies.append({
            "key": strategy_key,
            "name": strategy_info.get("name", strategy_key),
            "description": strategy_info.get("description", ""),
            "tactics": strategy_info.get("tactics", [])
        })
    
    return strategies


@router.get("/strategies/{strategy}", response_model=Dict)
async def get_strategy_info(strategy: str):
    """
    Get information about a specific strategy
    
    Args:
        strategy: Strategy key
        
    Returns:
        Strategy details
    """
    if strategy not in STRATEGIES:
        return {
            "error": "Strategy not found",
            "available_strategies": get_all_strategies()
        }
    
    strategy_info = STRATEGIES[strategy]
    return {
        "key": strategy,
        "name": strategy_info.get("name", strategy),
        "description": strategy_info.get("description", ""),
        "tactics": strategy_info.get("tactics", [])
    }


@router.get("/models", response_model=Dict)
async def get_supported_models():
    """
    Get supported LLM providers and models
    
    Returns:
        Dictionary of providers and their models
    """
    return {
        "providers": [
            {
                "name": "groq",
                "display_name": "Groq",
                "models": [
                    "llama-3.3-70b-versatile",
                    "llama-3.1-70b-versatile",
                    "mixtral-8x7b-32768"
                ],
                "default_model": "llama-3.3-70b-versatile"
            },
            {
                "name": "openai",
                "display_name": "OpenAI",
                "models": [
                    "gpt-4o",
                    "gpt-4o-mini",
                    "gpt-4-turbo"
                ],
                "default_model": "gpt-4o-mini"
            },
            {
                "name": "anthropic",
                "display_name": "Anthropic",
                "models": [
                    "claude-3-5-sonnet-20241022",
                    "claude-3-5-haiku-20241022"
                ],
                "default_model": "claude-3-5-sonnet-20241022"
            }
        ]
    }


@router.get("/metrics", response_model=List[Dict])
async def get_metrics():
    """
    Get available evaluation metrics
    
    Returns:
        List of metrics with descriptions
    """
    return [
        {
            "key": "role_fidelity",
            "name": "Role Fidelity Score",
            "description": "Measures how well the agent maintained its assigned role",
            "range": "0-1 (higher is better)"
        },
        {
            "key": "drift_index",
            "name": "Drift Index",
            "description": "Measures degree of role drift over the conversation",
            "range": "0-1 (lower is better)"
        },
        {
            "key": "ethical_deviation",
            "name": "Ethical Deviation Score",
            "description": "Measures violations of ethical constraints",
            "range": "0-1 (lower is better)"
        },
        {
            "key": "consistency",
            "name": "Consistency Score",
            "description": "Measures response consistency and lack of contradictions",
            "range": "0-1 (higher is better)"
        },
        {
            "key": "overall",
            "name": "Overall Score",
            "description": "Weighted average of all metrics",
            "range": "0-1 (higher is better)"
        }
    ]