"""
Experiment Logger - Logs experiment execution details
"""
import os
from datetime import datetime
from pathlib import Path


class ExperimentLogger:
    """Logger for experiment execution"""
    
    def __init__(self, experiment_id: str, experiment_name: str):
        """
        Initialize logger
        
        Args:
            experiment_id: Unique experiment ID
            experiment_name: Human-readable name
        """
        self.experiment_id = experiment_id
        self.experiment_name = experiment_name
        
        # Create logs directory
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Create log file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"experiment_{experiment_id}_{timestamp}.log"
        
        # Write header
        self._write_header()
    
    def _write_header(self):
        """Write log file header"""
        with open(self.log_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write(f"Red Team AI Experiment Log\n")
            f.write("="*80 + "\n")
            f.write(f"Experiment ID: {self.experiment_id}\n")
            f.write(f"Experiment Name: {self.experiment_name}\n")
            f.write(f"Start Time: {datetime.utcnow().isoformat()}\n")
            f.write("="*80 + "\n\n")
    
    def log(self, message: str):
        """
        Log a message
        
        Args:
            message: Message to log
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def log_turn(self, turn_number: int, query: str, response: str, strategy: str):
        """
        Log a conversation turn
        
        Args:
            turn_number: Turn number
            query: Interrogator query
            response: Target response
            strategy: Attack strategy used
        """
        with open(self.log_file, 'a') as f:
            f.write("\n" + "-"*80 + "\n")
            f.write(f"TURN {turn_number} (Strategy: {strategy})\n")
            f.write("-"*80 + "\n")
            f.write(f"Interrogator: {query}\n\n")
            f.write(f"Target: {response}\n")
            f.write("-"*80 + "\n")
    
    def log_scores(self, scores):
        """
        Log evaluation scores
        
        Args:
            scores: ScoreMetrics object
        """
        with open(self.log_file, 'a') as f:
            f.write("\n" + "="*80 + "\n")
            f.write("EVALUATION SCORES\n")
            f.write("="*80 + "\n")
            f.write(f"Overall Score: {scores.overall_score:.3f}\n")
            f.write(f"Role Fidelity: {scores.role_fidelity_score:.3f}\n")
            f.write(f"Drift Index: {scores.drift_index:.3f}\n")
            f.write(f"Ethical Deviation: {scores.ethical_deviation_score:.3f}\n")
            f.write(f"Consistency: {scores.consistency_score:.3f}\n")
            f.write("="*80 + "\n")