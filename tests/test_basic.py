"""
Example tests for Red Team AI
Run with: pytest tests/
"""
import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared import (
    AgentRole,
    ExperimentConfig,
    AttackStrategy,
    LLMProvider,
    validate_score
)


class TestSchemas:
    """Test data schemas"""
    
    def test_agent_role_creation(self):
        """Test creating an AgentRole"""
        role = AgentRole(
            name="Test Agent",
            description="Test description",
            persona="Test persona",
            constraints=["Test constraint"]
        )
        assert role.name == "Test Agent"
        assert len(role.constraints) == 1
    
    def test_experiment_config_defaults(self):
        """Test ExperimentConfig with defaults"""
        role = AgentRole(
            name="Test",
            description="Test",
            persona="Test",
            constraints=[]
        )
        config = ExperimentConfig(
            experiment_name="test",
            target_role=role
        )
        assert config.num_turns == 10
        assert config.temperature == 0.7
        assert config.target_llm_provider == LLMProvider.GROQ


class TestUtils:
    """Test utility functions"""
    
    def test_validate_score(self):
        """Test score validation"""
        assert validate_score(0.5) == 0.5
        assert validate_score(-0.1) == 0.0
        assert validate_score(1.5) == 1.0
        assert validate_score(0.0) == 0.0
        assert validate_score(1.0) == 1.0


class TestMetrics:
    """Test metric calculations"""
    
    def test_role_fidelity_calculation(self):
        """Test role fidelity metric"""
        from agents.judging_agent.metrics import MetricCalculator
        
        calc = MetricCalculator()
        score, analysis = calc.calculate_role_fidelity(
            role_description="Helpful customer service agent",
            role_constraints=["Never share personal info"],
            responses=["I'm here to help you!", "How can I assist?"],
            queries=["Help me", "What can you do?"]
        )
        
        assert 0.0 <= score <= 1.0
        assert isinstance(analysis, str)
    
    def test_drift_index_calculation(self):
        """Test drift index metric"""
        from agents.judging_agent.metrics import MetricCalculator
        
        calc = MetricCalculator()
        score, analysis = calc.calculate_drift_index(
            responses=["I'm a helpful agent", "I'm still helpful"],
            role_description="Helpful agent"
        )
        
        assert 0.0 <= score <= 1.0
        assert isinstance(analysis, str)


class TestStrategies:
    """Test attack strategies"""
    
    def test_get_all_strategies(self):
        """Test getting all strategies"""
        from agents.interrogator_agent import get_all_strategies
        
        strategies = get_all_strategies()
        assert len(strategies) > 0
        assert "role_drift" in strategies
    
    def test_get_strategy_prompt(self):
        """Test getting strategy prompt"""
        from agents.interrogator_agent import get_strategy_prompt
        
        prompt = get_strategy_prompt("role_drift")
        assert isinstance(prompt, str)
        assert len(prompt) > 0


# Integration tests (require API key)
@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set"
)
class TestIntegration:
    """Integration tests with actual LLM calls"""
    
    def test_end_to_end_experiment(self):
        """Test complete experiment flow"""
        from orchestrator import run_experiment
        
        role = AgentRole(
            name="Test Agent",
            description="A test agent",
            persona="Friendly",
            constraints=["Be helpful"]
        )
        
        config = ExperimentConfig(
            experiment_name="test_experiment",
            target_role=role,
            attack_strategies=[AttackStrategy.ROLE_DRIFT],
            num_turns=2  # Short test
        )
        
        result = run_experiment(config)
        
        assert result.experiment_id
        assert result.status
        assert len(result.conversation) == 2
        assert result.scores is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])