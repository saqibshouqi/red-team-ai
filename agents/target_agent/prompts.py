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
	conversation_history: List[dict],
	query: str
) -> str:
	"""
	Build a prompt that includes system prompt, conversation history, and the new query.
	"""
	history = "\n".join([
		f"User: {turn['user']}\nAgent: {turn['agent']}" for turn in conversation_history
	]) if conversation_history else ""
	return f"{system_prompt}\n{history}\nUser: {query}\nAgent:"
