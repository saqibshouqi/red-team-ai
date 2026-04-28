# Core schemas and enums for Red Team AI
from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class LLMProvider(str, Enum):
	GROQ = "groq"
	OPENAI = "openai"
	ANTHROPIC = "anthropic"

class AttackStrategy(str, Enum):
	ROLE_DRIFT = "role_drift"
	ETHICAL_PROBING = "ethical_probing"
	CONTRADICTION = "contradiction"
	CONFUSION = "confusion"
	AUTHORITY_CHALLENGE = "authority_challenge"
	EMOTIONAL_MANIPULATION = "emotional_manipulation"

class ExperimentStatus(str, Enum):
	PENDING = "pending"
	RUNNING = "running"
	COMPLETED = "completed"
	FAILED = "failed"

class AgentRole(BaseModel):
	name: str
	description: str
	persona: Optional[str] = None
	constraints: List[str] = []
	knowledge_domain: Optional[str] = None

class Message(BaseModel):
	sender: str
	content: str
	timestamp: Optional[str] = None

class ConversationTurn(BaseModel):
	turn_number: int
	interrogator_message: str
	target_response: str
	interrogator_strategy: str
	response_time_ms: Optional[float] = None
	timestamp: Optional[Any] = None

class ScoreMetrics(BaseModel):
	role_fidelity_score: float
	drift_index: float
	ethical_deviation_score: float
	consistency_score: float
	overall_score: float
	detailed_analysis: Optional[str] = None
	turn_by_turn_scores: Optional[List[Any]] = None

class ExperimentConfig(BaseModel):
	experiment_name: str
	description: Optional[str] = None
	target_role: AgentRole
	attack_strategies: List[AttackStrategy] = [AttackStrategy.ROLE_DRIFT]
	target_llm_provider: LLMProvider = LLMProvider.GROQ
	target_model: Optional[str] = None
	num_turns: int = 10
	temperature: float = 0.7
	max_tokens: int = 1024
	use_llm_judge: bool = False
	judge_llm_provider: Optional[LLMProvider] = None
	judge_model: Optional[str] = None
	interrogator_llm_provider: Optional[LLMProvider] = None
	interrogator_model: Optional[str] = None

class ExperimentResult(BaseModel):
	experiment_id: str
	experiment_name: str
	config: ExperimentConfig
	status: ExperimentStatus
	conversation: Optional[List[ConversationTurn]] = None
	scores: Optional[ScoreMetrics] = None
	start_time: Optional[Any] = None
	end_time: Optional[Any] = None
	duration_seconds: Optional[float] = None
	error_message: Optional[str] = None

class ExperimentCreateRequest(BaseModel):
	config: ExperimentConfig
	run_immediately: bool = True

class ExperimentListResponse(BaseModel):
	experiments: List[ExperimentResult]
	total: int
