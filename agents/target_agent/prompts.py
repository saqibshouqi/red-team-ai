# Prompts for Target Agent
from typing import List, Optional

def build_target_agent_system_prompt(
	role_name: str,
	role_description: str,
	persona: Optional[str] = None,
	constraints: Optional[List[str]] = None,
	knowledge_domain: Optional[str] = None
) -> str:
	"""
	Build the system prompt for the target agent based on its role and constraints.
	"""
	prompt = f"You are a {role_name}. {role_description}"
	if persona:
		prompt += f" Persona: {persona}."
	if knowledge_domain:
		prompt += f" Knowledge domain: {knowledge_domain}."
	if constraints:
		prompt += " Constraints: " + "; ".join(constraints)
	return prompt

def build_context_aware_prompt(
	system_prompt: str,
	conversation_history: List[dict]
) -> str:
	"""
	Build a system prompt that includes conversation history for context.
	Note: The current query is added separately as a user message.
	"""
	if not conversation_history:
		return system_prompt
	history = "\n".join([
		f"User: {turn['query']}\nAgent: {turn['response']}" for turn in conversation_history
	])
	return f"{system_prompt}\n\nPrevious conversation:\n{history}"
