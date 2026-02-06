# Core schemas and enums for Red Team AI
from enum import Enum
from typing import Any, Dict, List, Optional

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
    name: str = Field(description="Name of the role (e.g., 'Customer Support Agent')")
    description: str = Field(description="Detailed description of the role")
    persona: Optional[str] = Field(
        default=None, description="Personality traits and behavioral characteristics"
    )
    constraints: List[str] = Field(
        default_factory=list, description="List of constraints and boundaries"
    )
    knowledge_domain: Optional[str] = Field(
        default=None, description="Domain of expertise/knowledge"
    )


class Message(BaseModel):
    sender: str
    content: str
    timestamp: Optional[str] = None


class ConversationTurn(BaseModel):
    turn_number: int = Field(ge=1, description="Turn number (1-indexed)")
    interrogator_message: str = Field(description="Interrogator's query/message")
    target_response: str = Field(description="Target agent's response")
    interrogator_strategy: str = Field(description="Attack strategy used")
    response_time_ms: Optional[float] = Field(
        default=None, ge=0, description="Response time in milliseconds"
    )
    timestamp: Optional[str] = Field(
        default=None, description="ISO timestamp of the turn"
    )


class TurnScore(BaseModel):
    """Score for a single conversation turn"""

    turn: int
    role_fidelity: float
    ethical_deviation: float
    overall: float


class ScoreMetrics(BaseModel):
    role_fidelity_score: float = Field(
        ge=0.0, le=1.0, description="Role fidelity score (0-1)"
    )
    drift_index: float = Field(
        ge=0.0, le=1.0, description="Drift index (0-1, lower is better)"
    )
    ethical_deviation_score: float = Field(
        ge=0.0, le=1.0, description="Ethical deviation score (0-1, lower is better)"
    )
    consistency_score: float = Field(
        ge=0.0, le=1.0, description="Consistency score (0-1)"
    )
    overall_score: float = Field(
        ge=0.0, le=1.0, description="Overall composite score (0-1)"
    )
    detailed_analysis: Optional[str] = None
    turn_by_turn_scores: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="List of turn-by-turn score dictionaries"
    )


class ExperimentConfig(BaseModel):
    experiment_name: str = Field(description="Name of the experiment")
    description: Optional[str] = Field(
        default=None, description="Optional experiment description"
    )
    target_role: AgentRole = Field(description="Target agent role definition")
    attack_strategies: List[AttackStrategy] = Field(
        default=[AttackStrategy.ROLE_DRIFT],
        description="List of attack strategies to use",
    )
    target_llm_provider: LLMProvider = Field(
        default=LLMProvider.GROQ, description="LLM provider for target agent"
    )
    target_model: Optional[str] = Field(
        default=None, description="Model name for target agent"
    )
    num_turns: int = Field(
        default=10, ge=1, le=100, description="Number of conversation turns"
    )
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Sampling temperature"
    )
    max_tokens: int = Field(
        default=1024, ge=1, le=4096, description="Maximum tokens per response"
    )
    use_llm_judge: bool = Field(
        default=False, description="Whether to use LLM-as-judge"
    )
    judge_llm_provider: Optional[LLMProvider] = Field(
        default=None, description="LLM provider for judge"
    )
    judge_model: Optional[str] = Field(default=None, description="Model name for judge")
    interrogator_llm_provider: Optional[LLMProvider] = Field(
        default=None, description="LLM provider for interrogator"
    )
    interrogator_model: Optional[str] = Field(
        default=None, description="Model name for interrogator"
    )


class ExperimentResult(BaseModel):
    experiment_id: str = Field(description="Unique experiment identifier")
    experiment_name: str = Field(description="Name of the experiment")
    config: ExperimentConfig = Field(description="Experiment configuration")
    status: ExperimentStatus = Field(description="Current experiment status")
    conversation: Optional[List[ConversationTurn]] = Field(
        default=None, description="Conversation turns"
    )
    scores: Optional[ScoreMetrics] = Field(
        default=None, description="Evaluation scores"
    )
    start_time: Optional[str] = Field(
        default=None, description="ISO timestamp of experiment start"
    )
    end_time: Optional[str] = Field(
        default=None, description="ISO timestamp of experiment end"
    )
    duration_seconds: Optional[float] = Field(
        default=None, ge=0, description="Experiment duration in seconds"
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if experiment failed"
    )


class ExperimentCreateRequest(BaseModel):
    config: ExperimentConfig
    run_immediately: bool = True


class ExperimentListResponse(BaseModel):
    experiments: List[ExperimentResult]
    total: int
