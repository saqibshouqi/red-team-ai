"""
Shared modules for Red Team AI
"""

from .config_validator import (
    ConfigValidationError,
    check_environment_setup,
    validate_experiment_config,
    validate_llm_provider_config,
)
from .llm_client import LLMClient, get_llm_client
from .schemas import (
    AgentRole,
    AttackStrategy,
    ConversationTurn,
    ExperimentConfig,
    ExperimentCreateRequest,
    ExperimentListResponse,
    ExperimentResult,
    ExperimentStatus,
    LLMProvider,
    Message,
    ScoreMetrics,
)
from .utils import (
    calculate_duration,
    format_conversation_for_display,
    generate_id,
    get_logger,
    get_timestamp,
    load_json,
    save_json,
    setup_logging,
    truncate_text,
    validate_score,
)

__all__ = [
    # Schemas
    "LLMProvider",
    "AttackStrategy",
    "ExperimentStatus",
    "AgentRole",
    "Message",
    "ConversationTurn",
    "ScoreMetrics",
    "ExperimentConfig",
    "ExperimentResult",
    "ExperimentCreateRequest",
    "ExperimentListResponse",
    # LLM
    "LLMClient",
    "get_llm_client",
    # Utils
    "generate_id",
    "get_timestamp",
    "calculate_duration",
    "truncate_text",
    "save_json",
    "load_json",
    "format_conversation_for_display",
    "validate_score",
    "get_logger",
    "setup_logging",
    # Config validation
    "validate_llm_provider_config",
    "validate_experiment_config",
    "check_environment_setup",
    "ConfigValidationError",
]
