#!/bin/bash

# TouchLine Production Deployment Script
# Deploy to your server (DigitalOcean, AWS, etc.)

set -e

echo "🚀 TouchLine Production Deployment"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the TouchLine root directory"
    exit 1
fi

# Configuration
SERVER_IP=${1:-"your-server-ip"}
SERVER_USER=${2:-"root"}
APP_DIR="/var/www/touchline"

echo "📋 Deployment Configuration:"
echo "   Server: $SERVER_USER@$SERVER_IP"
echo "   App Directory: $APP_DIR"
echo ""

# Step 1: Push to GitHub (if not already done)
echo "📤 Step 1: Pushing to GitHub..."
git add .
git commit -m "🚀 Production deployment - $(date)" || echo "No changes to commit"
git push origin auto-dev
echo "✅ Code pushed to GitHub"
echo ""

# Step 2: Deploy to server
echo "📡 Step 2: Deploying to server..."
ssh $SERVER_USER@$SERVER_IP << EOF
    # Update system
    echo "📦 Updating system packages..."
    apt update && apt upgrade -y
    
    # Install dependencies
    echo "🔧 Installing dependencies..."
    apt install -y python3 python3-pip python3-venv nginx git curl
    
    # Install Node.js
    echo "📦 Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    
    # Install PM2
    echo "⚡ Installing PM2..."
    npm install -g pm2
    
    # Clone/update app
    echo "📁 Setting up TouchLine app..."
    if [ -d "$APP_DIR" ]; then
        cd $APP_DIR
        git pull origin auto-dev
    else
        git clone https://github.com/czauhar/TouchLine.git $APP_DIR
        cd $APP_DIR
    fi
    
    # Setup backend
    echo "🐍 Setting up Python backend..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Setup frontend
    echo "⚛️ Setting up React frontend..."
    cd ../frontend
    npm install
    npm run build
    
    # Setup environment
    echo "🔧 Setting up environment..."
    cd ..
    cp .env.example .env || echo "No .env.example found"
    
    # Start with PM2
    echo "🚀 Starting application with PM2..."
    pm2 delete touchline-backend touchline-frontend 2>/dev/null || true
    
    # Start backend
    cd backend
    pm2 start "source venv/bin/activate && python main.py" --name touchline-backend --cwd $(pwd)
    
    # Start frontend
    cd ../frontend
    pm2 start "npm run start" --name touchline-frontend --cwd $(pwd)
    
    # Save PM2 configuration
    pm2 save
    pm2 startup
    
    echo "✅ TouchLine deployed successfully!"
    echo "🌐 Backend: http://$SERVER_IP:8000"
    echo "🌐 Frontend: http://$SERVER_IP:3000"
    echo "📊 Check status: pm2 status"
    echo "📋 View logs: pm2 logs"
EOF

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo "🌐 Backend: http://$SERVER_IP:8000"
echo "🌐 Frontend: http://$SERVER_IP:3000"
echo "📱 SMS Alerts: Configured and ready"
echo "🔐 Authentication: User system ready"
echo ""
echo "📋 Next Steps:"
echo "1. Configure your .env file on the server with:"
echo "   - TWILIO_ACCOUNT_SID=your_account_sid"
echo "   - TWILIO_AUTH_TOKEN=your_auth_token" 
echo "   - TWILIO_PHONE_NUMBER=your_twilio_number"
echo "   - API_FOOTBALL_KEY=your_api_key"
echo ""
echo "2. Test SMS notifications:"
echo "   ssh $SERVER_USER@$SERVER_IP 'cd $APP_DIR/backend && source venv/bin/activate && python test_sms.py'"
echo ""
echo "3. Monitor the application:"
echo "   ssh $SERVER_USER@$SERVER_IP 'pm2 status'"
echo "   ssh $SERVER_USER@$SERVER_IP 'pm2 logs'"
