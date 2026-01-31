# Red Team AI

> Production-grade platform for evaluating Role-Playing Language Agents (RPLAs) using adversarial testing and automated scoring.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

Red Team AI is a modular, research-friendly platform that enables systematic evaluation of AI role-playing agents through adversarial interrogation. The system coordinates three specialized agents:

- **Target Agent**: The RPLA under evaluation, maintaining a defined role
- **Interrogator Agent**: Red team attacker using multiple strategies to test boundaries
- **Judging Agent**: Automated scorer providing quantitative metrics

## ✨ Features

- 🤖 **Multi-Agent Architecture**: Independent, extensible agent modules
- 🎭 **Multiple Attack Strategies**: Role drift, ethical probing, contradiction, confusion, authority challenge, emotional manipulation
- 📊 **Comprehensive Metrics**: Role fidelity, drift index, ethical deviation, consistency scores
- 🔌 **Multi-Provider Support**: Groq, OpenAI, Anthropic
- 💾 **Persistent Storage**: SQLite database with full experiment history
- 🌐 **REST API**: FastAPI backend with full CRUD operations
- 🖥️ **Interactive Dashboard**: React frontend for experiment management
- 📈 **Visualization**: Turn-by-turn metrics and conversation analysis
- 🔄 **Reproducible**: Complete experiment configuration and replay

## 🏗️ Architecture

```
red-team-ai/
├── backend/              # FastAPI server
│   ├── api/             # REST endpoints
│   ├── database/        # SQLAlchemy models & CRUD
│   ├── models/          # Data models
│   └── main.py          # Application entry
├── orchestrator/         # Experiment coordination
│   ├── orchestrator.py  # Main controller
│   ├── experiment_runner.py
│   └── logger.py
├── agents/              # Agent implementations
│   ├── target_agent/    # RPLA under test
│   ├── interrogator_agent/  # Red team attacker
│   └── judging_agent/   # Automated scorer
├── shared/              # Common utilities
│   ├── schemas.py       # Pydantic models
│   ├── llm_client.py    # LLM abstraction
│   └── utils.py
└── frontend/            # React dashboard
    └── src/
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Groq API Key (free at [groq.com](https://groq.com))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/red-team-ai.git
cd red-team-ai
```

2. **Backend Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

3. **Frontend Setup**
```bash
cd frontend
npm install
cd ..
```

### Running the Application

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
cd backend
python main.py
```
Backend runs at: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs at: http://localhost:3000

### Your First Experiment

1. Navigate to http://localhost:3000
2. Click "Create Experiment"
3. Define your target role:
   - **Name**: "Customer Support Agent"
   - **Description**: "Helpful e-commerce support representative"
   - **Persona**: "Friendly, patient, professional"
   - **Constraints**: 
     - Never share customer personal information
     - Always verify identity before account changes
4. Select attack strategies (e.g., "Role Drift", "Ethical Probing")
5. Configure: 10 turns, Groq provider, llama-3.3-70b model
6. Click "Create & Run Experiment"
7. View real-time results and metrics

## 📖 Usage

### Python API

```python
from shared import ExperimentConfig, AgentRole, AttackStrategy, LLMProvider
from orchestrator import run_experiment

# Define target role
role = AgentRole(
    name="Financial Advisor",
    description="Provides investment advice",
    persona="Professional, cautious, data-driven",
    constraints=[
        "Never guarantee returns",
        "Always disclose risks",
        "Must recommend diversification"
    ],
    knowledge_domain="Finance and investment"
)

# Configure experiment
config = ExperimentConfig(
    experiment_name="financial_advisor_test",
    description="Testing ethical boundaries",
    target_role=role,
    attack_strategies=[
        AttackStrategy.ETHICAL_PROBING,
        AttackStrategy.AUTHORITY_CHALLENGE
    ],
    target_llm_provider=LLMProvider.GROQ,
    target_model="llama-3.3-70b-versatile",
    num_turns=10,
    temperature=0.7
)

# Run experiment
result = run_experiment(config)

# Access results
print(f"Overall Score: {result.scores.overall_score}")
print(f"Role Fidelity: {result.scores.role_fidelity_score}")
print(f"Drift Index: {result.scores.drift_index}")
```

### REST API

**Create Experiment:**
```bash
curl -X POST http://localhost:8000/api/v1/experiments/ \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "experiment_name": "test_experiment",
      "target_role": {
        "name": "Support Agent",
        "description": "Customer support",
        "persona": "Helpful and friendly",
        "constraints": ["Protect user privacy"]
      },
      "attack_strategies": ["role_drift"],
      "num_turns": 5
    },
    "run_immediately": true
  }'
```

**List Experiments:**
```bash
curl http://localhost:8000/api/v1/experiments/
```

**Get Experiment:**
```bash
curl http://localhost:8000/api/v1/experiments/{experiment_id}
```

## 🔧 Configuration

### LLM Providers

Configure via environment variables:

```bash
# Groq (recommended for speed)
GROQ_API_KEY=your_key

# OpenAI
OPENAI_API_KEY=your_key

# Anthropic
ANTHROPIC_API_KEY=your_key
```

### Supported Models

**Groq:**
- llama-3.3-70b-versatile (recommended)
- llama-3.1-70b-versatile
- mixtral-8x7b-32768

**OpenAI:**
- gpt-4o
- gpt-4o-mini
- gpt-4-turbo

**Anthropic:**
- claude-3-5-sonnet-20241022
- claude-3-5-haiku-20241022

### Attack Strategies

1. **Role Drift**: Push agent to deviate from assigned role
2. **Ethical Probing**: Test constraint adherence and ethical boundaries
3. **Contradiction**: Induce contradictory statements
4. **Confusion**: Inject ambiguous, conflicting information
5. **Authority Challenge**: Challenge role authority and boundaries
6. **Emotional Manipulation**: Use emotional appeals to influence behavior

### Evaluation Metrics

- **Role Fidelity Score** (0-1): Maintenance of assigned role
- **Drift Index** (0-1): Progressive deviation from role (lower is better)
- **Ethical Deviation** (0-1): Constraint violations (lower is better)
- **Consistency Score** (0-1): Response consistency without contradictions
- **Overall Score** (0-1): Weighted composite score

## 🔌 Extending the Platform

### Adding a New Agent

```python
# agents/my_agent/agent.py
from shared import LLMClient

class MyAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def process(self, input_data):
        # Your logic here
        return output
```

### Adding a New Metric

```python
# agents/judging_agent/metrics.py
@staticmethod
def calculate_my_metric(responses):
    score = # calculation
    analysis = # analysis text
    return score, analysis
```

### Adding a New Attack Strategy

```python
# agents/interrogator_agent/strategies.py
STRATEGIES["my_strategy"] = {
    "name": "My Strategy",
    "description": "What it does",
    "tactics": [
        "Tactic 1",
        "Tactic 2"
    ]
}
```

## 📊 Database Schema

**Tables:**
- `experiments`: Experiment metadata and configuration
- `conversation_turns`: Individual turns with queries/responses
- `scores`: Evaluation metrics per experiment

Access database:
```bash
sqlite3 red_team_ai.db
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html
```

## 📚 Research Applications

- **Safety Research**: Evaluate agent robustness under adversarial conditions
- **Alignment Studies**: Test constraint adherence and value alignment
- **Behavioral Analysis**: Study role maintenance and drift patterns
- **Comparison Studies**: Benchmark different models and prompting strategies
- **Red Teaming**: Systematic discovery of failure modes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am 'Add my feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Submit a Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Anthropic for Claude API
- Groq for fast inference
- OpenAI for GPT models
- FastAPI framework
- React and Vite

## 📧 Contact

For questions or collaboration:
- Create an issue on GitHub and please reach out to us.

## 🗺️ Roadmap

- [ ] Advanced metrics (semantic similarity, embedding-based)
- [ ] LLM-as-judge evaluation mode
- [ ] Multi-agent scenarios
- [ ] Real-time streaming
- [ ] Cloud deployment templates
- [ ] Jupyter notebook examples
- [ ] Dataset export formats
- [ ] A/B testing framework

---

**Built with ❤️ for the AI Safety and Research community**