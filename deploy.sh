#!/bin/bash

# TouchLine DigitalOcean Deployment Script
# Run this on your DigitalOcean droplet

set -e

echo "🚀 Starting TouchLine deployment..."

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

# Create app directory
echo "📁 Setting up app directory..."
sudo mkdir -p /var/www/touchline
sudo chown $USER:$USER /var/www/touchline
cd /var/www/touchline

# Clone or copy your code here
# If using git:
# git clone https://github.com/yourusername/touchline.git .
# Or copy files manually

echo "✅ Deployment script completed!"
echo "📝 Next steps:"
echo "1. Copy your TouchLine files to /var/www/touchline"
echo "2. Run: ./setup-app.sh"
echo "3. Configure environment variables"
echo "4. Start the application" 