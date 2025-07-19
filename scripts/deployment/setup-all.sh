#!/bin/bash
set -e

# --- Backend Setup ---
BACKEND_DIR="backend"
PYTHON_VERSION=3.11.9

# Ensure pyenv is installed
if ! command -v pyenv &> /dev/null; then
  echo "pyenv not found. Installing with Homebrew..."
  brew install pyenv
fi

# Install Python 3.11 if not already installed
if ! pyenv versions --bare | grep -q "^$PYTHON_VERSION$"; then
  echo "Installing Python $PYTHON_VERSION with pyenv..."
  pyenv install $PYTHON_VERSION
fi

# Set local Python version for this project
pyenv local $PYTHON_VERSION

# Create backend venv
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
  echo "Creating backend virtual environment with Python $PYTHON_VERSION..."
  pyenv exec python -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo "✅ Backend Python environment ready!"

# --- Frontend Setup ---
FRONTEND_DIR="frontend"
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies..."
  npm install
fi
cd ..

echo "✅ Frontend Node.js environment ready!"

echo "🎉 All setup complete! To start both servers, run ./start-all.sh" 