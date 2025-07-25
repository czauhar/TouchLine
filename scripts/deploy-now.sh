#!/bin/bash

# TouchLine Quick Deployment Script
# Run this to deploy the app immediately

set -e

echo "🚀 TouchLine Quick Deployment Starting..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    print_error "Please run this script from the TouchLine root directory"
    exit 1
fi

# Backend setup
print_success "Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_warning "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
print_success "Installing Python dependencies..."
pip install -r requirements.txt

# Create database
print_success "Creating database..."
python3 -c "from app.models import Base; from app.database import engine; Base.metadata.create_all(bind=engine); print('Database created!')"

# Run database migration
print_success "Running database migration..."
python3 migrate_database.py

# Start backend
print_success "Starting backend server..."
python3 main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Test backend
if curl -s http://localhost:8000/health > /dev/null; then
    print_success "Backend is running!"
else
    print_error "Backend failed to start"
    exit 1
fi

# Frontend setup
print_success "Setting up frontend..."
cd frontend

# Install dependencies
print_success "Installing Node.js dependencies..."
npm install

# Build frontend
print_success "Building frontend..."
npm run build

# Start frontend
print_success "Starting frontend server..."
npm start &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 5

# Test frontend
if curl -s http://localhost:3000 > /dev/null; then
    print_success "Frontend is running!"
else
    print_error "Frontend failed to start"
    exit 1
fi

echo ""
print_success "🎉 TouchLine is now running!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "To stop the servers, run:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
print_warning "Remember to configure your .env files with real API keys for production!" 