"""
Main orchestrator for Red Team AI platform
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from typing import List, Optional
from shared import (
    ExperimentConfig,
    ExperimentResult,
    ExperimentStatus,
    get_logger
)
from .experiment_runner import ExperimentRunner, run_experiment
from .logger import ExperimentLogger

logger = get_logger(__name__)


class Orchestrator:
    """
    Main orchestrator that manages multiple experiments and provides
    a high-level interface for the platform
    """
    
    def __init__(self):
        """Initialize orchestrator"""
        self.experiments: dict = {}
        logger.info("Orchestrator initialized")
    
    def create_experiment(
        self,
        config: ExperimentConfig,
        run_immediately: bool = False
    ) -> str:
        """
        Create a new experiment
        
        Args:
            config: Experiment configuration
            run_immediately: Whether to run immediately
            
        Returns:
            Experiment ID
        """
        runner = ExperimentRunner(config)
        experiment_id = runner.experiment_id
        
        # Store experiment
        self.experiments[experiment_id] = {
            "runner": runner,
            "config": config,
            "result": None,
            "status": ExperimentStatus.PENDING
        }
        
        logger.info(f"Created experiment: {experiment_id}")
        
        # Run immediately if requested
        if run_immediately:
            result = self.run_experiment(experiment_id)
            return experiment_id
        
        return experiment_id
    
    def run_experiment(self, experiment_id: str) -> ExperimentResult:
        """
        Run an experiment
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            ExperimentResult
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        exp_data = self.experiments[experiment_id]
        exp_data["status"] = ExperimentStatus.RUNNING
        
        logger.info(f"Running experiment: {experiment_id}")
        
        try:
            runner = exp_data["runner"]
            result = runner.run()
            
            exp_data["result"] = result
            exp_data["status"] = result.status
            
            return result
            
        except Exception as e:
            logger.error(f"Experiment execution failed: {e}")
            exp_data["status"] = ExperimentStatus.FAILED
            raise
    
    def get_experiment(self, experiment_id: str) -> Optional[ExperimentResult]:
        """Get experiment result"""
        if experiment_id not in self.experiments:
            return None
        return self.experiments[experiment_id].get("result")
    
    def list_experiments(self) -> List[dict]:
        """List all experiments"""
        experiments = []
        for exp_id, exp_data in self.experiments.items():
            experiments.append({
                "experiment_id": exp_id,
                "experiment_name": exp_data["config"].experiment_name,
                "status": exp_data["status"],
                "has_result": exp_data["result"] is not None
            })
        return experiments
    
    def delete_experiment(self, experiment_id: str) -> bool:
        """Delete an experiment"""
        if experiment_id in self.experiments:
            del self.experiments[experiment_id]
            logger.info(f"Deleted experiment: {experiment_id}")
            return True
        return False


# Global orchestrator instance
_orchestrator = None


def get_orchestrator() -> Orchestrator:
    """Get global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator