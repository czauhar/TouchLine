#!/bin/bash

# TouchLine Deployment Package
# Run this script on your DigitalOcean server

set -e

echo "🚀 Starting TouchLine deployment on DigitalOcean..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "🔧 Installing dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx git curl certbot python3-certbot-nginx

# Install Node.js (for frontend)
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2 for process management
echo "⚡ Installing PM2..."
sudo npm install -g pm2

# Clone and setup app
echo "📁 Cloning TouchLine app..."
cd /var/www
sudo rm -rf touchline
sudo git clone https://github.com/czauhar/TouchLine.git touchline
sudo chown -R $USER:$USER touchline
cd touchline

# Setup application
echo "🔧 Setting up application..."
chmod +x scripts/deployment/setup-app.sh scripts/deployment/start-production.sh
./scripts/deployment/setup-app.sh

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/touchline << EOF
server {
    listen 80;
    server_name 68.183.59.147;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/touchline /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Start application
echo "🚀 Starting application..."
./scripts/deployment/start-production.sh

echo "✅ TouchLine deployed successfully!"
echo "🌐 Backend: http://68.183.59.147:8000"
echo "🌐 Frontend: http://68.183.59.147:3000"
echo "📊 Check status: pm2 status"
echo "📋 View logs: pm2 logs"
