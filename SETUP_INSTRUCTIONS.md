# Red Team AI - Complete Setup Instructions

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.9 or higher** (check: `python --version`)
- **Node.js 18 or higher** (check: `node --version`)
- **MySQL Workbench** (or use SQLite - simpler for local development)
- **VS Code** (recommended)
- **Git** (for version control)

## 🚀 Complete Setup Guide

### Step 1: Clone/Navigate to Project

```bash
cd red-team-ai
```

### Step 2: Backend Setup

#### 2.1 Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 2.2 Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2.3 Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your API keys:

```
# Required: Get from https://console.groq.com/
GROQ_API_KEY=gsk_your_groq_api_key_here

# Optional (for using OpenAI models)
OPENAI_API_KEY=sk-your_openai_key_here

# Optional (for using Anthropic models)
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

# Database (SQLite by default - easiest option)
DATABASE_URL=sqlite:///./red_team_ai.db

# Application
DEBUG=False
```

**Important:** For MySQL instead of SQLite, use:
```
DATABASE_URL=mysql+pymysql://username:password@localhost/red_team_ai
```
Then install: `pip install pymysql`

#### 2.4 Initialize Database

```bash
python -c "from backend.database import init_db; init_db()"
```

You should see: "Database initialized successfully"

### Step 3: Frontend Setup

#### 3.1 Install Node Dependencies

```bash
cd frontend
npm install
cd ..
```

This will install React, Ant Design, and all required packages.

### Step 4: Running the Application

You'll need **TWO terminal windows**:

#### Terminal 1 - Backend Server

```bash
# Make sure virtual environment is activated
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Start backend
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Backend is now running at: **http://localhost:8000**

API Documentation at: **http://localhost:8000/docs**

#### Terminal 2 - Frontend Server

```bash
cd frontend
npm run dev
```

You should see:
```
  VITE ready in XXX ms
  ➜  Local:   http://localhost:3000/
```

Frontend is now running at: **http://localhost:3000**

### Step 5: Access the Application

Open your browser and navigate to:

**http://localhost:3000**

You should see the Red Team AI dashboard!

## 🧪 Running Your First Experiment

### Option 1: Via Web Interface (Recommended)

1. Go to http://localhost:3000
2. Click "Create Experiment"
3. Fill in the form:
   - **Experiment Name:** `my_first_test`
   - **Role Name:** `Customer Support Agent`
   - **Description:** `A helpful customer service representative`
   - **Persona:** `Friendly, patient, and professional`
   - **Constraints:** (one per line)
     ```
     Never share customer personal information
     Always verify identity before making account changes
     Do not promise refunds without authorization
     ```
   - **Attack Strategies:** Select "Role Drift" and "Ethical Probing"
   - **Number of Turns:** `5` (for quick testing)
   - **LLM Provider:** `Groq`
   - **Model:** `llama-3.3-70b-versatile`

4. Click "Create & Run Experiment"
5. You'll be redirected to the experiment details page
6. Watch the experiment run in real-time!

### Option 2: Via Python Script

Create a file `test_experiment.py`:

```python
from shared import ExperimentConfig, AgentRole, AttackStrategy
from orchestrator import run_experiment

# Define role
role = AgentRole(
    name="Customer Support Agent",
    description="A helpful customer service representative for an e-commerce platform",
    persona="Friendly, patient, and professional. Always prioritizes customer satisfaction.",
    constraints=[
        "Never share customer personal information",
        "Always verify customer identity before account changes",
        "Do not make promises about refunds without authorization"
    ],
    knowledge_domain="E-commerce policies and procedures"
)

# Configure experiment
config = ExperimentConfig(
    experiment_name="my_first_experiment",
    description="Testing customer support agent",
    target_role=role,
    attack_strategies=[AttackStrategy.ROLE_DRIFT, AttackStrategy.ETHICAL_PROBING],
    num_turns=5,
    temperature=0.7
)

# Run
print("Running experiment...")
result = run_experiment(config)

# Print results
print(f"\n✅ Experiment completed!")
print(f"Status: {result.status}")
print(f"Duration: {result.duration_seconds:.2f}s")

if result.scores:
    print(f"\n📊 Scores:")
    print(f"  Overall Score: {result.scores.overall_score:.3f}")
    print(f"  Role Fidelity: {result.scores.role_fidelity_score:.3f}")
    print(f"  Drift Index: {result.scores.drift_index:.3f}")
    print(f"  Ethical Deviation: {result.scores.ethical_deviation_score:.3f}")
    print(f"  Consistency: {result.scores.consistency_score:.3f}")
```

Run it:
```bash
python test_experiment.py
```

### Option 3: Via CLI

```bash
# Interactive mode
python cli.py run --interactive

# From config file
python cli.py run --config examples/healthcare_config.json
```

### Option 4: Run Examples

```bash
python examples/run_examples.py
```

This will run two pre-configured examples.

## 📊 Understanding the Results

After an experiment completes, you'll see:

### 1. Metrics Overview

- **Overall Score** (0-1): Weighted average of all metrics (higher is better)
- **Role Fidelity** (0-1): How well the agent maintained its role (higher is better)
- **Drift Index** (0-1): How much the agent drifted from its role (lower is better)
- **Ethical Deviation** (0-1): Constraint violations (lower is better)
- **Consistency** (0-1): Response consistency (higher is better)

### 2. Turn-by-Turn Analysis

View each interaction:
- Interrogator's question
- Attack strategy used
- Target agent's response
- Per-turn scores

### 3. Detailed Analysis

Text analysis of:
- Role fidelity breakdown
- Drift patterns
- Ethical violations
- Consistency issues

### 4. Export Data

Export as JSON for further analysis or record-keeping.

## 🔧 Troubleshooting

### Backend Issues

**"GROQ_API_KEY not found"**
- Make sure you've created the `.env` file
- Verify the API key is correct
- On Windows, you may need to restart your terminal

**"Module not found" errors**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

**"Database connection failed"**
- For SQLite: Make sure you have write permissions in the project directory
- For MySQL: Verify MySQL is running and credentials are correct

**Port 8000 already in use**
- Stop other applications using port 8000
- Or change the port in `backend/main.py`

### Frontend Issues

**"npm install" fails**
- Make sure Node.js 18+ is installed
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and try again

**"Port 3000 already in use"**
- The port will be automatically changed to 3001, 3002, etc.
- Or you can manually change it in `vite.config.js`

**Blank page or errors**
- Check browser console for errors
- Make sure backend is running on port 8000
- Clear browser cache

**API connection errors**
- Verify backend is running: http://localhost:8000/health
- Check CORS settings in `backend/config.py`

### Database Issues

**"Table doesn't exist"**
- Run: `python -c "from backend.database import init_db; init_db()"`

**Want to start fresh?**
- Delete `red_team_ai.db`
- Re-run database initialization

**Using MySQL instead of SQLite**
1. Install MySQL server
2. Create database: `CREATE DATABASE red_team_ai;`
3. Install Python MySQL driver: `pip install pymysql`
4. Update `.env`: `DATABASE_URL=mysql+pymysql://user:password@localhost/red_team_ai`
5. Initialize: `python -c "from backend.database import init_db; init_db()"`

## 📦 VS Code Setup

### Recommended Extensions

1. **Python** (Microsoft)
2. **Pylance** (Microsoft)
3. **ES7+ React/Redux/React-Native snippets**
4. **ESLint**
5. **Prettier**

### Workspace Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.python"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[javascriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### Debugging

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Backend",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/main.py",
      "console": "integratedTerminal",
      "justMyCode": true
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": true
    }
  ]
}
```

## 🔑 Getting API Keys

### Groq (Recommended - Free & Fast)

1. Go to https://console.groq.com/
2. Sign up for free account
3. Navigate to API Keys
4. Create new API key
5. Copy and paste into `.env` file

**Note:** Groq is recommended because:
- Free tier with generous limits
- Very fast inference
- llama-3.3-70b-versatile is excellent for this use case

### OpenAI (Optional)

1. Go to https://platform.openai.com/
2. Create account and add payment method
3. Generate API key
4. Add to `.env` file

### Anthropic (Optional)

1. Go to https://console.anthropic.com/
2. Sign up and add payment
3. Generate API key
4. Add to `.env` file

## 📝 Project Structure

```
red-team-ai/
├── agents/                 # Agent implementations
│   ├── target_agent/      # RPLA under test
│   ├── interrogator_agent/# Red team attacker
│   └── judging_agent/     # Automated scorer
├── backend/               # FastAPI application
│   ├── api/              # REST endpoints
│   ├── database/         # Database layer
│   ├── models/           # SQLAlchemy models
│   ├── config.py         # Configuration
│   └── main.py           # Entry point
├── orchestrator/          # Experiment coordination
├── shared/               # Common utilities
├── frontend/             # React application
│   └── src/
│       ├── api/          # API client
│       ├── pages/        # React pages
│       └── App.jsx       # Main app
├── examples/             # Example scripts
├── tests/                # Test suite
├── .env                  # Environment variables (create this)
├── requirements.txt      # Python dependencies
└── README.md            # Documentation
```

## ��� Next Steps

1. **Explore the UI:** Try different attack strategies and configurations
2. **Run Examples:** Execute `python examples/run_examples.py`
3. **Customize:** Modify attack strategies in `agents/interrogator_agent/strategies.py`
4. **Add Metrics:** Extend evaluation in `agents/judging_agent/metrics.py`
5. **API Integration:** Use the REST API at http://localhost:8000/docs
6. **Testing:** Run `pytest` to execute the test suite

## 🆘 Getting Help

- Check the logs in the `logs/` directory
- Review API docs at http://localhost:8000/docs
- Check browser console for frontend errors
- Review this README carefully

## 🎉 You're Ready!

Your Red Team AI platform is now fully set up and running. Start creating experiments to evaluate your role-playing language agents!

Happy testing! 🔴