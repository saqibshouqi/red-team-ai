"""
Target Agent Module
"""
from .agent import TargetAgent, create_target_agent
from .prompts import build_target_agent_system_prompt, build_context_aware_prompt

__all__ = [
    "TargetAgent",
    "create_target_agent",
    "build_target_agent_system_prompt",
    "build_context_aware_prompt"
]