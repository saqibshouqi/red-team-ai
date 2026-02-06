"""
Experiment Runner - Coordinates agents and executes experiments
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
import uuid
from typing import List
from datetime import datetime

from shared import (
    ExperimentConfig,
    ExperimentResult,
    ExperimentStatus,
    ConversationTurn,
    ScoreMetrics,
    get_llm_client,
    get_logger
)
from agents.target_agent import TargetAgent
from agents.interrogator_agent import InterrogatorAgent
from agents.judging_agent import JudgingAgent

logger = get_logger(__name__)


class ExperimentRunner:
    """
    Coordinates the execution of an experiment by managing interactions
    between Target, Interrogator, and Judging agents.
    """

    def __init__(self, config: ExperimentConfig):
        """
        Initialize experiment runner

        Args:
            config: Experiment configuration
        """
        self.config = config
        self.experiment_id = str(uuid.uuid4())

        # Initialize LLM clients
        self.target_llm = get_llm_client(
            provider=config.target_llm_provider.value,
            model=config.target_model
        )

        interrogator_provider = config.interrogator_llm_provider or config.target_llm_provider
        interrogator_model = config.interrogator_model or config.target_model
        self.interrogator_llm = get_llm_client(
            provider=interrogator_provider.value,
            model=interrogator_model
        )

        judge_llm = None
        if config.use_llm_judge:
            judge_provider = config.judge_llm_provider or config.target_llm_provider
            judge_model = config.judge_model or config.target_model
            judge_llm = get_llm_client(
                provider=judge_provider.value,
                model=judge_model
            )

        # Initialize agents
        self.target_agent = TargetAgent(
            role=config.target_role,
            llm_client=self.target_llm,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )

        self.interrogator_agent = InterrogatorAgent(
            llm_client=self.interrogator_llm,
            strategies=[s.value for s in config.attack_strategies],
            temperature=config.temperature + 0.1,  # Slightly more creative
            max_tokens=512
        )

        self.judging_agent = JudgingAgent(
            llm_client=judge_llm,
            use_llm_judge=config.use_llm_judge,
            temperature=0.3,  # Lower temperature for consistent judging
            max_tokens=1024
        )

        logger.info(f"Experiment runner initialized: {self.experiment_id}")

    def run(self) -> ExperimentResult:
        """
        Execute the experiment

        Returns:
            ExperimentResult with conversation and scores
        """
        start_time = datetime.now()
        conversation: List[ConversationTurn] = []

        logger.info(f"Starting experiment: {self.experiment_id}")

        try:
            # Run conversation turns
            previous_responses = []
            for turn_num in range(1, self.config.num_turns + 1):
                logger.info(f"Turn {turn_num}/{self.config.num_turns}")

                # Interrogator generates attack message
                interrogator_message, strategy = self.interrogator_agent.generate_query(
                    target_role=self.config.target_role,
                    turn_number=turn_num,
                    previous_responses=previous_responses
                )

                # Target agent responds
                turn_start = time.time()
                target_response = self.target_agent.respond(query=interrogator_message)
                response_time_ms = (time.time() - turn_start) * 1000

                # Store response for next turn
                previous_responses.append(target_response)

                # Record turn
                turn = ConversationTurn(
                    turn_number=turn_num,
                    interrogator_message=interrogator_message,
                    target_response=target_response,
                    interrogator_strategy=strategy,
                    response_time_ms=response_time_ms,
                    timestamp=datetime.now().isoformat()
                )
                conversation.append(turn)

                logger.debug(f"Turn {turn_num} completed")

            # Evaluate conversation
            logger.info("Evaluating conversation...")
            queries = [t.interrogator_message for t in conversation]
            responses = [t.target_response for t in conversation]
            strategies_used = [t.interrogator_strategy for t in conversation]

            scores = self.judging_agent.evaluate_conversation(
                role=self.config.target_role,
                queries=queries,
                responses=responses,
                strategies_used=strategies_used
            )

            end_time = datetime.now()
            duration_seconds = (end_time - start_time).total_seconds()

            result = ExperimentResult(
                experiment_id=self.experiment_id,
                experiment_name=self.config.experiment_name,
                config=self.config,
                status=ExperimentStatus.COMPLETED,
                conversation=conversation,
                scores=scores,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration_seconds=duration_seconds
            )

            logger.info(f"Experiment completed: {self.experiment_id} ({duration_seconds:.2f}s)")
            return result

        except Exception as e:
            logger.error(f"Experiment failed: {e}", exc_info=True)
            end_time = datetime.now()
            duration_seconds = (end_time - start_time).total_seconds()

            return ExperimentResult(
                experiment_id=self.experiment_id,
                experiment_name=self.config.experiment_name,
                config=self.config,
                status=ExperimentStatus.FAILED,
                conversation=conversation,
                scores=None,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration_seconds=duration_seconds,
                error_message=str(e)
            )


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
