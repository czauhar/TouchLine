#!/bin/bash
set -e

# --- Start Backend ---
echo "🚀 Starting backend server..."
cd backend
source venv/bin/activate
# Start FastAPI backend in background
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# --- Start Frontend ---
echo "🎨 Starting frontend dev server..."
cd frontend
npm run dev

# --- Cleanup on exit ---
echo "🛑 Stopping backend server..."
kill $BACKEND_PID 