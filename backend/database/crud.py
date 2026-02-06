"""
CRUD operations for database
"""
import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from backend.models.experiment import (
    ConversationTurnModel,
    Experiment,
    ExperimentStatusEnum,
    Score,
)
from shared import ConversationTurn, ExperimentResult, ExperimentStatus, ScoreMetrics


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """
    Parse ISO string timestamp to datetime object

    Args:
        value: ISO string timestamp or None

    Returns:
        datetime object or None
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            # Try parsing ISO format
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            # Fallback to other formats if needed
            try:
                return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                try:
                    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    return None

    return None


def serialize_conversation(conversation: Optional[List[ConversationTurn]]) -> Optional[List[dict]]:
    """
    Convert conversation from Pydantic models to list of dicts for JSON storage

    Args:
        conversation: List of ConversationTurn Pydantic models

    Returns:
        List of dictionaries or None
    """
    if not conversation:
        return None

    return [
        {
            "turn_number": turn.turn_number,
            "interrogator_message": turn.interrogator_message,
            "target_response": turn.target_response,
            "interrogator_strategy": turn.interrogator_strategy,
            "response_time_ms": turn.response_time_ms,
            "timestamp": turn.timestamp
        }
        for turn in conversation
    ]


def serialize_scores(scores: Optional[ScoreMetrics]) -> Optional[dict]:
    """
    Convert scores from Pydantic model to dict for JSON storage

    Args:
        scores: ScoreMetrics Pydantic model

    Returns:
        Dictionary with all score fields or None
    """
    if not scores:
        return None

    return {
        "role_fidelity_score": scores.role_fidelity_score,
        "drift_index": scores.drift_index,
        "ethical_deviation_score": scores.ethical_deviation_score,
        "consistency_score": scores.consistency_score,
        "overall_score": scores.overall_score,
        "detailed_analysis": scores.detailed_analysis,
        "turn_by_turn_scores": scores.turn_by_turn_scores
    }


def create_experiment(db: Session, result: ExperimentResult) -> Experiment:
    """
    Create new experiment in database

    Args:
        db: Database session
        result: ExperimentResult object

    Returns:
        Created Experiment model
    """
    # Map status
    status_map = {
        ExperimentStatus.PENDING: ExperimentStatusEnum.PENDING,
        ExperimentStatus.RUNNING: ExperimentStatusEnum.RUNNING,
        ExperimentStatus.COMPLETED: ExperimentStatusEnum.COMPLETED,
        ExperimentStatus.FAILED: ExperimentStatusEnum.FAILED
    }

    experiment = Experiment(
        id=result.experiment_id,
        name=result.experiment_name,
        description=result.config.description,
        status=status_map[result.status],
        config=result.config.model_dump(mode='json'),
        conversation=serialize_conversation(result.conversation),
        scores=serialize_scores(result.scores),
        start_time=parse_datetime(result.start_time),
        end_time=parse_datetime(result.end_time),
        duration_seconds=result.duration_seconds,
        error_message=result.error_message
    )

    db.add(experiment)
    db.commit()
    db.refresh(experiment)

    # Create conversation turns
    if result.conversation:
        for turn in result.conversation:
            turn_model = ConversationTurnModel(
                experiment_id=result.experiment_id,
                turn_number=turn.turn_number,
                interrogator_message=turn.interrogator_message,
                target_response=turn.target_response,
                interrogator_strategy=turn.interrogator_strategy,
                response_time_ms=turn.response_time_ms,
                timestamp=parse_datetime(turn.timestamp) if turn.timestamp else datetime.utcnow()
            )
            db.add(turn_model)

    # Create scores
    if result.scores:
        score_model = Score(
            experiment_id=result.experiment_id,
            role_fidelity_score=result.scores.role_fidelity_score,
            drift_index=result.scores.drift_index,
            ethical_deviation_score=result.scores.ethical_deviation_score,
            consistency_score=result.scores.consistency_score,
            overall_score=result.scores.overall_score,
            detailed_analysis=result.scores.detailed_analysis,
            turn_by_turn_scores=result.scores.turn_by_turn_scores
        )
        db.add(score_model)

    db.commit()

    return experiment


def get_experiment(db: Session, experiment_id: str) -> Optional[Experiment]:
    """Get experiment by ID"""
    return db.query(Experiment).filter(Experiment.id == experiment_id).first()


def get_experiments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[ExperimentStatusEnum] = None
) -> List[Experiment]:
    """
    Get list of experiments

    Args:
        db: Database session
        skip: Number to skip (pagination)
        limit: Maximum number to return
        status: Filter by status

    Returns:
        List of experiments
    """
    query = db.query(Experiment)

    if status:
        query = query.filter(Experiment.status == status)

    return query.order_by(Experiment.created_at.desc()).offset(skip).limit(limit).all()


def update_experiment_status(
    db: Session,
    experiment_id: str,
    status: ExperimentStatusEnum,
    end_time: Optional[datetime] = None,
    duration: Optional[float] = None,
    error_message: Optional[str] = None
) -> Optional[Experiment]:
    """
    Update experiment status

    Args:
        db: Database session
        experiment_id: Experiment ID
        status: New status
        end_time: End time (datetime object or ISO string)
        duration: Duration in seconds
        error_message: Error message if failed

    Returns:
        Updated experiment or None
    """
    experiment = get_experiment(db, experiment_id)

    if not experiment:
        return None

    experiment.status = status

    if end_time:
        experiment.end_time = parse_datetime(end_time) if isinstance(end_time, str) else end_time

    if duration:
        experiment.duration_seconds = duration

    if error_message:
        experiment.error_message = error_message

    db.commit()
    db.refresh(experiment)

    return experiment


def delete_experiment(db: Session, experiment_id: str) -> bool:
    """Delete experiment and related data"""
    experiment = get_experiment(db, experiment_id)

    if not experiment:
        return False

    # Delete related data
    db.query(ConversationTurnModel).filter(
        ConversationTurnModel.experiment_id == experiment_id
    ).delete()

    db.query(Score).filter(
        Score.experiment_id == experiment_id
    ).delete()

    # Delete experiment
    db.delete(experiment)
    db.commit()

    return True


def get_experiment_scores(db: Session, experiment_id: str) -> Optional[Score]:
    """Get scores for an experiment"""
    return db.query(Score).filter(Score.experiment_id == experiment_id).first()


def get_conversation_turns(
    db: Session,
    experiment_id: str
) -> List[ConversationTurnModel]:
    """Get all conversation turns for an experiment"""
    return db.query(ConversationTurnModel).filter(
        ConversationTurnModel.experiment_id == experiment_id
    ).order_by(ConversationTurnModel.turn_number).all()


def get_experiments_count(db: Session, status: Optional[ExperimentStatusEnum] = None) -> int:
    """Get total count of experiments"""
    query = db.query(Experiment)

    if status:
        query = query.filter(Experiment.status == status)

    return query.count()
