"""
Shared utility functions
"""
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


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
    """Get configured logger"""
    return logging.getLogger(name)