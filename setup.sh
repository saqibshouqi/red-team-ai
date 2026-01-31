#!/bin/bash
# Setup script for Red Team AI

echo "🔴 Red Team AI - Setup Script"
echo "=============================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys"
fi

# Initialize database
echo ""
echo "Initializing database..."
python -c "from backend.database import init_db; init_db()"

# Setup frontend
echo ""
echo "Setting up frontend..."
cd frontend
npm install
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GROQ_API_KEY"
echo "2. Start backend: source venv/bin/activate && cd backend && python main.py"
echo "3. Start frontend (new terminal): cd frontend && npm run dev"
echo "4. Open http://localhost:3000"
echo ""