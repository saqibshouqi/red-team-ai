# Quick Start Guide

Get Red Team AI running in 5 minutes!

## Prerequisites

- Python 3.9+
- Node.js 18+
- Groq API Key (free at [groq.com](https://groq.com))

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/red-team-ai.git
cd red-team-ai

# Run setup script
./setup.sh

# Add your API key to .env
echo "GROQ_API_KEY=your_key_here" >> .env
```

### Option 2: Manual Setup

```bash
# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..

# Environment
cp .env.example .env
# Edit .env and add GROQ_API_KEY
```

## Running

### Terminal 1 - Backend
```bash
source venv/bin/activate
cd backend
python main.py
```

Backend runs at: http://localhost:8000

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

Frontend runs at: http://localhost:3000

## Your First Experiment

### Via Web Interface

1. Open http://localhost:3000
2. Click "Create Experiment"
3. Fill in the form:
   - **Experiment Name**: `my_first_test`
   - **Role Name**: `Customer Support Agent`
   - **Description**: `Helps customers with orders`
   - **Persona**: `Friendly and helpful`
   - **Constraints**: `Never share customer data`
   - **Strategies**: Select "Role Drift"
   - **Turns**: `5`
4. Click "Create & Run Experiment"
5. View results!

### Via Python Script

```python
from shared import ExperimentConfig, AgentRole, AttackStrategy
from orchestrator import run_experiment

# Define role
role = AgentRole(
    name="Support Agent",
    description="Helps with customer issues",
    persona="Friendly and professional",
    constraints=["Protect customer privacy"]
)

# Configure experiment
config = ExperimentConfig(
    experiment_name="first_test",
    target_role=role,
    attack_strategies=[AttackStrategy.ROLE_DRIFT],
    num_turns=5
)

# Run
result = run_experiment(config)
print(f"Score: {result.scores.overall_score}")
```

### Via CLI

```bash
# Interactive mode
python cli.py run --interactive

# From config file
python cli.py run --config examples/config.json
```

## Example Experiments

Run the provided examples:

```bash
source venv/bin/activate
python examples/run_examples.py
```

This will run:
1. Customer Support Agent test
2. Financial Advisor test

## Viewing Results

- **Web Dashboard**: http://localhost:3000/experiments
- **API**: http://localhost:8000/docs
- **Files**: Results saved as JSON in working directory

## Next Steps

- Read the full [README.md](README.md)
- Explore [example scripts](examples/)
- Check [API documentation](http://localhost:8000/docs)
- Customize attack strategies in `agents/interrogator_agent/strategies.py`
- Add custom metrics in `agents/judging_agent/metrics.py`

## Troubleshooting

### "GROQ_API_KEY not found"
- Make sure you've added your API key to `.env`
- Source your environment: `source .env`

### Backend won't start
- Check Python version: `python --version` (need 3.9+)
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend won't start
- Check Node version: `node --version` (need 18+)
- Clear cache: `cd frontend && rm -rf node_modules && npm install`

### Database errors
- Delete `red_team_ai.db` and restart backend

## Getting Help

- Check [documentation](README.md)
- Open an [issue](https://github.com/yourusername/red-team-ai/issues)
- Read [Contributing Guide](CONTRIBUTING.md)

Happy red teaming! 🔴