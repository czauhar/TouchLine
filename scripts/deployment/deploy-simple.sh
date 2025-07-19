#!/bin/bash

# TouchLine Simple Deployment Script
# Run this on your DigitalOcean droplet

set -e

echo "🚀 Starting TouchLine simple deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "🔧 Installing dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx git curl

# Install Node.js (for frontend)
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2 for process management
echo "⚡ Installing PM2..."
sudo npm install -g pm2

# Clone and setup app
echo "📁 Cloning TouchLine app..."
cd /var/www
git clone https://github.com/czauhar/TouchLine.git touchline
cd touchline

# Setup application
echo "🔧 Setting up application..."
chmod +x setup-app.sh start-production.sh
./setup-app.sh

# Start application
echo "🚀 Starting application..."
./start-production.sh

echo "✅ TouchLine deployed successfully!"
echo "🌐 Backend: http://your-server-ip:8000"
echo "🌐 Frontend: http://your-server-ip:3000"
echo "📊 Check status: pm2 status" 