#!/bin/bash

# TouchLine Production Start Script
# Run this to start the application in production

set -e

echo "🚀 Starting TouchLine in production mode..."

# Navigate to app directory
cd /var/www/touchline

# Stop existing processes
echo "🛑 Stopping existing processes..."
pm2 stop touchline-backend touchline-frontend 2>/dev/null || true
pm2 delete touchline-backend touchline-frontend 2>/dev/null || true

# Start backend with PM2
echo "🐍 Starting backend..."
cd backend
source venv/bin/activate
pm2 start "python main.py" --name "touchline-backend" --cwd /var/www/touchline/backend

# Start frontend with PM2
echo "⚛️ Starting frontend..."
cd ../frontend
pm2 start "npm start" --name "touchline-frontend" --cwd /var/www/touchline/frontend

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup

echo "✅ TouchLine started in production!"
echo "📊 Check status with: pm2 status"
echo "📋 View logs with: pm2 logs"
echo "🌐 Backend running on: http://your-server-ip:8000"
echo "🌐 Frontend running on: http://your-server-ip:3000" 