"""
API routes for experiments
"""

import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import (
    create_experiment,
    delete_experiment,
    get_db,
    get_experiment,
    get_experiments,
    get_experiments_count,
)
from backend.models.experiment import ExperimentStatusEnum
from orchestrator import get_orchestrator, run_experiment
from shared import (
    ExperimentConfig,
    ExperimentCreateRequest,
    ExperimentResult,
    ExperimentStatus,
)

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
            run_immediately=False,  # We'll handle running separately
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

        db_experiment = create_experiment(db, initial_result)

        # If run_immediately, execute in background
        if request.run_immediately:
            background_tasks.add_task(run_experiment_background, experiment_id, db)
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
    """
    List experiments

    Args:
        skip: Number to skip (pagination)
        limit: Maximum number to return
        status: Filter by status
        db: Database session

    Returns:
        List of experiments
    """
    try:
        # Map status string to enum
        status_enum = None
        if status:
            try:
                status_enum = ExperimentStatusEnum(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

        experiments = get_experiments(db, skip=skip, limit=limit, status=status_enum)
        total = get_experiments_count(db, status=status_enum)

        # Convert to dict
        experiments_data = []
        for exp in experiments:
            experiments_data.append(
                {
                    "id": exp.id,
                    "name": exp.name,
                    "description": exp.description,
                    "status": exp.status.value,
                    "start_time": (
                        exp.start_time.isoformat() if exp.start_time else None
                    ),
                    "end_time": exp.end_time.isoformat() if exp.end_time else None,
                    "duration_seconds": exp.duration_seconds,
                    "created_at": exp.created_at.isoformat(),
                    "overall_score": (
                        exp.scores.get("overall_score") if exp.scores else None
                    ),
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
    """
    Get experiment details

    Args:
        experiment_id: Experiment ID
        db: Database session

    Returns:
        Experiment details
    """
    experiment = get_experiment(db, experiment_id)

    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    # Build response
    return {
        "id": experiment.id,
        "name": experiment.name,
        "description": experiment.description,
        "status": experiment.status.value,
        "config": experiment.config,
        "conversation": experiment.conversation,
        "scores": experiment.scores,
        "start_time": (
            experiment.start_time.isoformat() if experiment.start_time else None
        ),
        "end_time": experiment.end_time.isoformat() if experiment.end_time else None,
        "duration_seconds": experiment.duration_seconds,
        "error_message": experiment.error_message,
        "created_at": experiment.created_at.isoformat(),
    }


@router.post("/{experiment_id}/run", response_model=dict)
async def run_existing_experiment(
    experiment_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """
    Run or rerun an existing experiment.

    This endpoint can be used to:
    - Run a pending experiment for the first time
    - Rerun a completed or failed experiment with the same configuration

    Args:
        experiment_id: Experiment ID
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Status message
    """
    experiment = get_experiment(db, experiment_id)

    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if experiment.status == ExperimentStatusEnum.RUNNING:
        raise HTTPException(status_code=400, detail="Experiment already running")

    # Run in background (supports rerunning from database)
    background_tasks.add_task(run_experiment_background, experiment_id, db)

    return {
        "experiment_id": experiment_id,
        "status": "running",
        "message": "Experiment started. Results will be updated when complete.",
    }


@router.delete("/{experiment_id}", response_model=dict)
async def delete_experiment_endpoint(experiment_id: str, db: Session = Depends(get_db)):
    """
    Delete an experiment

    Args:
        experiment_id: Experiment ID
        db: Database session

    Returns:
        Success message
    """
    success = delete_experiment(db, experiment_id)

    if not success:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return {"message": "Experiment deleted successfully"}


@router.get("/{experiment_id}/export", response_model=dict)
async def export_experiment(
    experiment_id: str, format: str = "json", db: Session = Depends(get_db)
):
    """
    Export experiment data

    Args:
        experiment_id: Experiment ID
        format: Export format (json or csv)
        db: Database session

    Returns:
        Exported data
    """
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
            "start_time": (
                experiment.start_time.isoformat() if experiment.start_time else None
            ),
            "end_time": (
                experiment.end_time.isoformat() if experiment.end_time else None
            ),
            "duration_seconds": experiment.duration_seconds,
            "created_at": experiment.created_at.isoformat(),
        }
    else:
        raise HTTPException(
            status_code=400, detail="Only JSON format supported currently"
        )


def run_experiment_background(experiment_id: str, db: Session):
    """
    Run experiment in background and update database.
    Supports rerunning experiments by loading config from database.

    Args:
        experiment_id: Experiment ID
        db: Database session
    """
    fresh_db = SessionLocal()
    try:
        from backend.database import parse_datetime
        from backend.database.crud import serialize_conversation, serialize_scores
        from orchestrator.experiment_runner import ExperimentRunner

        # Load experiment from database
        from shared import get_logger

        logger = get_logger(__name__)

        experiment = get_experiment(fresh_db, experiment_id)
        if not experiment:
            logger.error(f"Experiment {experiment_id} not found in database")
            return

        # Update status to running
        experiment.status = ExperimentStatusEnum.RUNNING
        fresh_db.commit()

        # Reconstruct ExperimentConfig from stored config
        try:
            config_dict = experiment.config
            if not config_dict:
                raise ValueError("Experiment config not found")

            # Convert config dict back to ExperimentConfig Pydantic model
            from shared import ExperimentConfig

            config = ExperimentConfig(**config_dict)

            # Create new experiment runner with the config
            runner = ExperimentRunner(config)

            # Run the experiment
            result = runner.run()

            # Update database with results
            status_map = {
                ExperimentStatus.COMPLETED: ExperimentStatusEnum.COMPLETED,
                ExperimentStatus.FAILED: ExperimentStatusEnum.FAILED,
                ExperimentStatus.RUNNING: ExperimentStatusEnum.RUNNING,
                ExperimentStatus.PENDING: ExperimentStatusEnum.PENDING,
            }

            experiment.status = status_map[result.status]
            experiment.conversation = serialize_conversation(result.conversation)
            experiment.scores = serialize_scores(result.scores)
            experiment.start_time = parse_datetime(result.start_time)
            experiment.end_time = parse_datetime(result.end_time)
            experiment.duration_seconds = result.duration_seconds
            experiment.error_message = result.error_message
            fresh_db.commit()

            logger.info(f"Experiment {experiment_id} completed successfully")

        except Exception as e:
            error_msg = str(e)
            logger.error(
                f"Error running experiment {experiment_id}: {error_msg}", exc_info=True
            )

            # Check if it's a rate limit error and provide helpful message
            if (
                "rate limit" in error_msg.lower()
                or "429" in error_msg
                or "rate_limit" in error_msg.lower()
                or "tokens per day" in error_msg.lower()
            ):
                error_msg = (
                    "⚠️ Rate Limit Exceeded: The LLM provider (Groq) has reached its daily token limit. "
                    "The experiment could not complete because there are not enough tokens remaining. "
                    "\n\nSolutions:\n"
                    "• Wait for the rate limit to reset (check logs for exact time)\n"
                    "• Use a different LLM provider (OpenAI, Anthropic)\n"
                    "• Reduce experiment size (fewer turns, shorter responses)\n"
                    "• Upgrade your Groq account tier\n\n"
                    f"Original error: {error_msg}"
                )
            elif "timeout" in error_msg.lower():
                error_msg = (
                    "⏱️ Request Timeout: The LLM provider took too long to respond. "
                    "Please try again later or use a different provider/model. "
                    f"\n\nOriginal error: {error_msg}"
                )

            # Update status to failed with detailed error message
            experiment.status = ExperimentStatusEnum.FAILED
            experiment.error_message = error_msg
            fresh_db.commit()

    finally:
        fresh_db.close()


from backend.database.connection import SessionLocal
