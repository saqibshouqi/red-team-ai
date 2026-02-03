"""
CRUD operations for database
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import json

from backend.models.experiment import (
    Experiment,
    ConversationTurnModel,
    Score,
    ExperimentStatusEnum
)
from shared import ExperimentResult, ExperimentStatus


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
        conversation=json.loads(result.model_dump_json())['conversation'] if result.conversation else None,
        scores=result.scores.model_dump() if result.scores else None,
        start_time=result.start_time,
        end_time=result.end_time,
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
                timestamp=turn.timestamp
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
    """Update experiment status"""
    experiment = get_experiment(db, experiment_id)
    
    if not experiment:
        return None
    
    experiment.status = status
    
    if end_time:
        experiment.end_time = end_time
    
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