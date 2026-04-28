"""
Configuration validation utilities
"""
import os
from typing import Optional, List
from .schemas import LLMProvider, ExperimentConfig, AgentRole
from .utils import get_logger

logger = get_logger(__name__)


class ConfigValidationError(Exception):
    """Raised when configuration validation fails"""
    pass


def validate_llm_provider_config(provider: str, model: Optional[str] = None) -> tuple[str, Optional[str]]:
    """
    Validate and normalize LLM provider configuration

    Args:
        provider: Provider name
        model: Optional model name

    Returns:
        Tuple of (normalized_provider, validated_model)

    Raises:
        ConfigValidationError: If configuration is invalid
    """
    provider_lower = provider.lower()

    # Validate provider
    try:
        validated_provider = LLMProvider(provider_lower).value
    except ValueError:
        raise ConfigValidationError(
            f"Invalid LLM provider: {provider}. "
            f"Supported providers: {[p.value for p in LLMProvider]}"
        )

    # Set default model if not provided
    if not model:
        model = get_default_model(validated_provider)
        logger.info(f"Using default model for {validated_provider}: {model}")

    # Validate API key exists
    api_key = get_api_key_for_provider(validated_provider)
    if not api_key:
        raise ConfigValidationError(
            f"API key not found for provider {validated_provider}. "
            f"Please set {get_env_key_name(validated_provider)} environment variable."
        )

    return validated_provider, model


def get_default_model(provider: str) -> str:
    """Get default model for a provider"""
    defaults = {
        "groq": "llama-3.3-70b-versatile",
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-5-haiku-20241022"
    }
    return defaults.get(provider.lower(), defaults["groq"])


def get_api_key_for_provider(provider: str) -> Optional[str]:
    """Get API key for a provider from environment"""
    env_key = get_env_key_name(provider)
    return os.getenv(env_key)


def get_env_key_name(provider: str) -> str:
    """Get environment variable name for API key"""
    mapping = {
        "groq": "GROQ_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY"
    }
    return mapping.get(provider.lower(), f"{provider.upper()}_API_KEY")


def validate_experiment_config(config: ExperimentConfig) -> List[str]:
    """
    Validate experiment configuration and return list of warnings

    Args:
        config: Experiment configuration to validate

    Returns:
        List of warning messages (empty if no warnings)
    """
    warnings = []

    # Validate target role
    if not config.target_role.name or not config.target_role.name.strip():
        warnings.append("Target role name is empty")

    if not config.target_role.description or not config.target_role.description.strip():
        warnings.append("Target role description is empty")

    # Validate attack strategies
    if not config.attack_strategies:
        warnings.append("No attack strategies specified - experiment may not be effective")

    # Validate number of turns
    if config.num_turns < 3:
        warnings.append("Very few turns (<3) may not provide meaningful evaluation")
    elif config.num_turns > 50:
        warnings.append("Many turns (>50) may result in long execution times")

    # Validate temperature
    if config.temperature < 0.1:
        warnings.append("Very low temperature (<0.1) may result in repetitive responses")
    elif config.temperature > 1.5:
        warnings.append("Very high temperature (>1.5) may result in inconsistent responses")

    # Validate max_tokens
    if config.max_tokens < 50:
        warnings.append("Very low max_tokens (<50) may truncate responses")
    elif config.max_tokens > 2048:
        warnings.append("Very high max_tokens (>2048) may result in long response times")

    # Check for LLM judge configuration
    if config.use_llm_judge:
        if not config.judge_llm_provider:
            warnings.append("LLM judge enabled but no judge provider specified - will use target provider")
        if not config.judge_model:
            warnings.append("LLM judge enabled but no judge model specified - will use target model")

    # Validate provider configurations
    try:
        validate_llm_provider_config(
            config.target_llm_provider.value,
            config.target_model
        )
    except ConfigValidationError as e:
        warnings.append(f"Target LLM configuration issue: {str(e)}")

    if config.interrogator_llm_provider:
        try:
            validate_llm_provider_config(
                config.interrogator_llm_provider.value,
                config.interrogator_model
            )
        except ConfigValidationError as e:
            warnings.append(f"Interrogator LLM configuration issue: {str(e)}")

    if config.use_llm_judge and config.judge_llm_provider:
        try:
            validate_llm_provider_config(
                config.judge_llm_provider.value,
                config.judge_model
            )
        except ConfigValidationError as e:
            warnings.append(f"Judge LLM configuration issue: {str(e)}")

    return warnings


def check_environment_setup() -> dict:
    """
    Check environment setup and return status

    Returns:
        Dictionary with environment check results
    """
    status = {
        "providers_configured": {},
        "missing_keys": [],
        "warnings": []
    }

    for provider in LLMProvider:
        provider_value = provider.value
        env_key = get_env_key_name(provider_value)
        api_key = os.getenv(env_key)

        status["providers_configured"][provider_value] = api_key is not None

        if not api_key:
            status["missing_keys"].append(env_key)

    # Check database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        status["warnings"].append("DATABASE_URL not set - using default SQLite")

    # Check debug mode
    debug = os.getenv("DEBUG", "false").lower() == "true"
    if debug:
        status["warnings"].append("Debug mode is enabled")

    return status
