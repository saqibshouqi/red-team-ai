"""
API routes for experiments
"""

import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db, create_experiment, get_experiment, get_experiments, delete_experiment, get_experiments_count
from backend.database.connection import SessionLocal
from backend.database.crud import serialize_conversation, serialize_scores, parse_datetime
from backend.models.experiment import ExperimentStatusEnum
from shared import (
    ExperimentConfig,
    ExperimentCreateRequest,
    ExperimentResult,
    ExperimentStatus,
    get_logger,
)
from orchestrator import get_orchestrator

logger = get_logger(__name__)

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.post("/", response_model=dict)
async def create_new_experiment(
    request: ExperimentCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Create a new experiment

    Args:
        request: Experiment configuration and run flag
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Experiment ID and status
    """
    try:
        # Create experiment using orchestrator
        orchestrator = get_orchestrator()
        experiment_id = orchestrator.create_experiment(
            config=request.config,
            run_immediately=False,
        )

        # Create initial database record
        initial_result = ExperimentResult(
            experiment_id=experiment_id,
            experiment_name=request.config.experiment_name,
            config=request.config,
            status=ExperimentStatus.PENDING,
            conversation=[],
            scores=None,
            start_time=None,
            end_time=None,
            duration_seconds=None,
        )

        create_experiment(db, initial_result)

        if request.run_immediately:
            background_tasks.add_task(run_experiment_background, experiment_id)
            return {
                "experiment_id": experiment_id,
                "status": "running",
                "message": "Experiment started",
            }

        return {
            "experiment_id": experiment_id,
            "status": "pending",
            "message": "Experiment created",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=dict)
async def list_experiments(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    try:
        status_enum = None
        if status:
            try:
                status_enum = ExperimentStatusEnum(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

        experiments = get_experiments(db, skip=skip, limit=limit, status=status_enum)
        total = get_experiments_count(db, status=status_enum)

        experiments_data = []
        for exp in experiments:
            experiments_data.append(
                {
                    "id": exp.id,
                    "name": exp.name,
                    "description": exp.description,
                    "status": exp.status.value,
                    "start_time": exp.start_time.isoformat() if exp.start_time else None,
                    "end_time": exp.end_time.isoformat() if exp.end_time else None,
                    "duration_seconds": exp.duration_seconds,
                    "created_at": exp.created_at.isoformat(),
                    "overall_score": exp.scores.get("overall_score") if exp.scores else None,
                }
            )

        return {
            "experiments": experiments_data,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{experiment_id}", response_model=dict)
async def get_experiment_details(experiment_id: str, db: Session = Depends(get_db)):
    experiment = get_experiment(db, experiment_id)

    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return {
        "id": experiment.id,
        "name": experiment.name,
        "description": experiment.description,
        "status": experiment.status.value,
        "config": experiment.config,
        "conversation": experiment.conversation,
        "scores": experiment.scores,
        "start_time": experiment.start_time.isoformat() if experiment.start_time else None,
        "end_time": experiment.end_time.isoformat() if experiment.end_time else None,
        "duration_seconds": experiment.duration_seconds,
        "error_message": experiment.error_message,
        "created_at": experiment.created_at.isoformat(),
    }


@router.post("/{experiment_id}/run", response_model=dict)
async def run_existing_experiment(
    experiment_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    experiment = get_experiment(db, experiment_id)

    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if experiment.status == ExperimentStatusEnum.RUNNING:
        raise HTTPException(status_code=400, detail="Experiment already running")

    background_tasks.add_task(run_experiment_background, experiment_id)

    return {
        "experiment_id": experiment_id,
        "status": "running",
        "message": "Experiment started",
    }


@router.delete("/{experiment_id}", response_model=dict)
async def delete_experiment_endpoint(experiment_id: str, db: Session = Depends(get_db)):
    success = delete_experiment(db, experiment_id)

    if not success:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return {"message": "Experiment deleted successfully"}


@router.get("/{experiment_id}/export", response_model=dict)
async def export_experiment(
    experiment_id: str,
    format: str = "json",
    db: Session = Depends(get_db),
):
    experiment = get_experiment(db, experiment_id)

    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if format == "json":
        return {
            "id": experiment.id,
            "name": experiment.name,
            "description": experiment.description,
            "status": experiment.status.value,
            "config": experiment.config,
            "conversation": experiment.conversation,
            "scores": experiment.scores,
            "start_time": experiment.start_time.isoformat() if experiment.start_time else None,
            "end_time": experiment.end_time.isoformat() if experiment.end_time else None,
            "duration_seconds": experiment.duration_seconds,
            "created_at": experiment.created_at.isoformat(),
        }
    else:
        raise HTTPException(status_code=400, detail="Only JSON format supported currently")


def run_experiment_background(experiment_id: str):
    """
    Run experiment in background and update database.

    Args:
        experiment_id: Experiment ID
    """
    fresh_db = SessionLocal()
    try:
        experiment = get_experiment(fresh_db, experiment_id)
        if not experiment:
            logger.error(f"Experiment {experiment_id} not found in database")
            return

        # Mark as running
        experiment.status = ExperimentStatusEnum.RUNNING
        experiment.start_time = datetime.utcnow()
        fresh_db.commit()

        # Reconstruct ExperimentConfig from stored JSON
        config = ExperimentConfig(**experiment.config)

        # Run via orchestrator
        orchestrator = get_orchestrator()
        orchestrator.create_experiment(config=config, run_immediately=False)
        result = orchestrator.run_experiment(experiment_id)

        # Save results back to DB
        experiment = get_experiment(fresh_db, experiment_id)
        if experiment:
            status_map = {
                ExperimentStatus.COMPLETED: ExperimentStatusEnum.COMPLETED,
                ExperimentStatus.FAILED: ExperimentStatusEnum.FAILED,
                ExperimentStatus.RUNNING: ExperimentStatusEnum.RUNNING,
                ExperimentStatus.PENDING: ExperimentStatusEnum.PENDING,
            }
            experiment.status = status_map.get(result.status, ExperimentStatusEnum.FAILED)
            experiment.conversation = serialize_conversation(result.conversation)
            experiment.scores = serialize_scores(result.scores)
            experiment.start_time = parse_datetime(result.start_time) if result.start_time else experiment.start_time
            experiment.end_time = parse_datetime(result.end_time) if result.end_time else datetime.utcnow()
            experiment.duration_seconds = result.duration_seconds
            experiment.error_message = result.error_message
            fresh_db.commit()

    except Exception as e:
        logger.error(f"Background experiment failed: {e}")
        try:
            experiment = get_experiment(fresh_db, experiment_id)
            if experiment:
                experiment.status = ExperimentStatusEnum.FAILED
                experiment.error_message = str(e)
                fresh_db.commit()
        except Exception:
            pass
    finally:
        fresh_db.close()
