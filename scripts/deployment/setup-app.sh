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
# Database Configuration
DATABASE_URL=sqlite:///./touchline.db

# JWT Configuration
SECRET_KEY=your-production-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Twilio Configuration (for SMS)
TWILIO_ACCOUNT_SID=your-twilio-account-sid-here
TWILIO_AUTH_TOKEN=your-twilio-auth-token-here
TWILIO_PHONE_NUMBER=your-twilio-phone-number-here

# Sports API Configuration
API_FOOTBALL_KEY=your-api-football-key-here
SPORTS_API_BASE_URL=https://v3.football.api-sports.io/

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

EOF

# Create frontend environment file
echo "📝 Creating frontend environment file..."
cd ../frontend
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://your-domain.com:8000
NEXTAUTH_SECRET=your-production-nextauth-secret
NEXTAUTH_URL=http://your-domain.com
EOF

echo "✅ App setup completed!"
echo "📝 Next steps:"
echo "1. Edit backend/.env with your API credentials"
echo "2. Edit frontend/.env.local with your domain"
echo "3. Run: ./start-production.sh" 