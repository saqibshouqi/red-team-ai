"""
Experiment Runner - Executes multi-turn red team experiments
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from typing import Optional
from datetime import datetime
import time

from shared import (
    ExperimentConfig,
    ExperimentResult,
    ExperimentStatus,
    ConversationTurn,
    ScoreMetrics,
    generate_id,
    get_logger
)
from agents.target_agent import create_target_agent
from agents.interrogator_agent import create_interrogator_agent
from agents.judging_agent import create_judging_agent
from .logger import ExperimentLogger

logger = get_logger(__name__)


class ExperimentRunner:
    """
    Runs a complete red team experiment by coordinating agents
    """
    
    def __init__(self, config: ExperimentConfig):
        """
        Initialize experiment runner
        
        Args:
            config: Experiment configuration
        """
        self.config = config
        self.experiment_id = generate_id()
        self.logger = ExperimentLogger(self.experiment_id, config.experiment_name)
        
        logger.info(f"Initialized experiment: {self.experiment_id}")
    
    def run(self) -> ExperimentResult:
        """
        Run the complete experiment
        
        Returns:
            ExperimentResult with conversation and scores
        """
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting experiment: {self.config.experiment_name}")
            self.logger.log(f"Experiment started: {self.config.experiment_name}")
            
            # Initialize agents
            target_agent = self._create_target_agent()
            interrogator_agent = self._create_interrogator_agent()
            judging_agent = self._create_judging_agent()
            
            # Run conversation
            conversation = self._run_conversation(target_agent, interrogator_agent)
            
            # Evaluate conversation
            scores = self._evaluate_conversation(judging_agent, conversation)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Build result
            result = ExperimentResult(
                experiment_id=self.experiment_id,
                experiment_name=self.config.experiment_name,
                config=self.config,
                status=ExperimentStatus.COMPLETED,
                conversation=conversation,
                scores=scores,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration
            )
            
            logger.info(f"Experiment completed: {self.experiment_id}")
            logger.info(f"Overall score: {scores.overall_score:.3f}")
            self.logger.log(f"Experiment completed successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Experiment failed: {e}")
            self.logger.log(f"Experiment failed: {str(e)}")
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return ExperimentResult(
                experiment_id=self.experiment_id,
                experiment_name=self.config.experiment_name,
                config=self.config,
                status=ExperimentStatus.FAILED,
                conversation=[],
                scores=None,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                error_message=str(e)
            )
    
    def _create_target_agent(self):
        """Create target agent"""
        logger.info("Creating target agent")
        return create_target_agent(
            role=self.config.target_role,
            provider=self.config.target_llm_provider.value,
            model=self.config.target_model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
    
    def _create_interrogator_agent(self):
        """Create interrogator agent"""
        logger.info("Creating interrogator agent")
        
        provider = self.config.interrogator_llm_provider or self.config.target_llm_provider
        model = self.config.interrogator_model or self.config.target_model
        
        return create_interrogator_agent(
            provider=provider.value,
            model=model,
            strategies=[s.value for s in self.config.attack_strategies],
            temperature=self.config.temperature,
            max_tokens=512  # Shorter for queries
        )
    
    def _create_judging_agent(self):
        """Create judging agent"""
        logger.info("Creating judging agent")
        
        provider = self.config.judge_llm_provider
        model = self.config.judge_model
        
        if provider and model:
            return create_judging_agent(
                provider=provider.value,
                model=model,
                use_llm_judge=self.config.use_llm_judge
            )
        else:
            # Rule-based only
            return create_judging_agent(use_llm_judge=False)
    
    def _run_conversation(self, target_agent, interrogator_agent) -> list:
        """Run multi-turn conversation"""
        logger.info(f"Running {self.config.num_turns} turn conversation")
        self.logger.log(f"Starting {self.config.num_turns} turn conversation")
        
        conversation = []
        previous_responses = []
        
        for turn in range(1, self.config.num_turns + 1):
            logger.info(f"Turn {turn}/{self.config.num_turns}")
            
            turn_start = time.time()
            
            # Interrogator generates query
            query, strategy = interrogator_agent.generate_query(
                target_role=self.config.target_role,
                turn_number=turn,
                previous_responses=previous_responses
            )
            
            # Target responds
            response = target_agent.respond(query)
            previous_responses.append(response)
            
            turn_time = (time.time() - turn_start) * 1000  # milliseconds
            
            # Log turn
            turn_data = ConversationTurn(
                turn_number=turn,
                interrogator_message=query,
                target_response=response,
                interrogator_strategy=strategy,
                response_time_ms=turn_time,
                timestamp=datetime.utcnow()
            )
            
            conversation.append(turn_data)
            
            self.logger.log_turn(turn, query, response, strategy)
        
        return conversation
    
    def _evaluate_conversation(self, judging_agent, conversation) -> ScoreMetrics:
        """Evaluate the conversation"""
        logger.info("Evaluating conversation")
        self.logger.log("Starting evaluation")
        
        # Extract queries and responses
        queries = [turn.interrogator_message for turn in conversation]
        responses = [turn.target_response for turn in conversation]
        strategies = [turn.interrogator_strategy for turn in conversation]
        
        # Evaluate
        scores = judging_agent.evaluate_conversation(
            role=self.config.target_role,
            queries=queries,
            responses=responses,
            strategies_used=strategies
        )
        
        self.logger.log_scores(scores)
        
        return scores


def run_experiment(config: ExperimentConfig) -> ExperimentResult:
    """
    Convenience function to run an experiment
    
    Args:
        config: Experiment configuration
        
    Returns:
        ExperimentResult
    """
    runner = ExperimentRunner(config)
    return runner.run()