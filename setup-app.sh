#!/bin/bash

# TouchLine App Setup Script
# Run this after copying files to /var/www/touchline

set -e

echo "🔧 Setting up TouchLine application..."

# Navigate to app directory
cd /var/www/touchline

# Set up backend
echo "🐍 Setting up Python backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up frontend
echo "⚛️ Setting up React frontend..."
cd ../frontend
npm install

# Build frontend for production
echo "🏗️ Building frontend..."
npm run build

# Create production environment file
echo "📝 Creating production environment file..."
cd ../backend
cat > .env << EOF
# Database
DATABASE_URL=sqlite:///./touchline.db

# Twilio SMS (add your credentials)
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here

# Sports API (add your API key)
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=api-football-v1.p.rapidapi.com

# Server settings
HOST=0.0.0.0
PORT=8000
EOF

echo "✅ App setup completed!"
echo "📝 Next steps:"
echo "1. Edit backend/.env with your API credentials"
echo "2. Run: ./start-production.sh" 