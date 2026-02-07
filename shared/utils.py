"""
Shared utility functions
"""
import json
import logging
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


# Setup logging with better formatting
def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """
    Setup logging configuration

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # Setup file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)

    # Prevent duplicate logs
    root_logger.propagate = False

# Initialize logging with default settings
setup_logging()


def generate_id() -> str:
    """Generate unique ID for experiments"""
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """Get current timestamp as ISO string"""
    return datetime.utcnow().isoformat()


def calculate_duration(start_time: datetime, end_time: datetime) -> float:
    """Calculate duration in seconds between two timestamps"""
    return (end_time - start_time).total_seconds()


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def save_json(data: Any, filepath: str) -> None:
    """Save data as JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def load_json(filepath: str) -> Any:
    """Load data from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def format_conversation_for_display(turns: List[Dict]) -> str:
    """Format conversation turns for readable display"""
    output = []
    for i, turn in enumerate(turns, 1):
        output.append(f"\n{'='*60}")
        output.append(f"Turn {i}")
        output.append(f"{'='*60}")
        output.append(f"\n🔴 Interrogator:\n{turn.get('interrogator_message', '')}")
        output.append(f"\n🎯 Target:\n{turn.get('target_response', '')}")
    return "\n".join(output)


def validate_score(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Validate and clamp score to valid range"""
    return max(min_val, min(max_val, score))


def get_logger(name: str) -> logging.Logger:
    """
    Get configured logger with context

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Add context formatter if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
