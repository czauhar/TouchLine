#!/bin/bash

# TouchLine DigitalOcean Quick Deployment Script
# Run this on your DigitalOcean droplet

set -e

echo "🚀 TouchLine DigitalOcean Deployment"
echo "===================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)
print_info "Server IP: $SERVER_IP"

# Update system
print_success "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
print_success "Installing dependencies..."
apt install -y python3 python3-pip python3-venv nginx git curl

# Install Node.js
print_success "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Install PM2
print_success "Installing PM2..."
npm install -g pm2

# Clone repository
print_success "Cloning TouchLine repository..."
cd /var/www
rm -rf touchline
git clone https://github.com/czauhar/TouchLine.git touchline
chown -R $USER:$USER touchline
cd touchline

# Setup backend
print_success "Setting up Python backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create production environment file
print_success "Creating production environment file..."
cat > .env << EOF
# Database Configuration
DATABASE_URL=sqlite:///./touchline.db

# JWT Configuration
SECRET_KEY=your-production-secret-key-change-this-$(date +%s)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Twilio Configuration (for SMS alerts)
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

# Setup frontend
print_success "Setting up React frontend..."
cd ../frontend
npm install
npm run build

# Create frontend environment file
print_success "Creating frontend environment file..."
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://$SERVER_IP:8000
NEXTAUTH_SECRET=your-production-nextauth-secret-$(date +%s)
NEXTAUTH_URL=http://$SERVER_IP:3000
EOF

# Configure Nginx
print_success "Configuring Nginx..."
tee /etc/nginx/sites-available/touchline << EOF
server {
    listen 80;
    server_name $SERVER_IP;

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
ln -sf /etc/nginx/sites-available/touchline /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# Start application with PM2
print_success "Starting application with PM2..."
cd /var/www/touchline

# Stop existing processes
pm2 stop touchline-backend touchline-frontend 2>/dev/null || true
pm2 delete touchline-backend touchline-frontend 2>/dev/null || true

# Start backend
cd backend
source venv/bin/activate
pm2 start "python main.py" --name "touchline-backend" --cwd /var/www/touchline/backend

# Start frontend
cd ../frontend
pm2 start "npm start" --name "touchline-frontend" --cwd /var/www/touchline/frontend

# Save PM2 configuration
pm2 save
pm2 startup

# Wait for services to start
sleep 10

# Test deployment
print_success "Testing deployment..."

# Test backend
if curl -s http://localhost:8000/health > /dev/null; then
    print_success "Backend is running!"
else
    print_error "Backend failed to start"
    pm2 logs touchline-backend
    exit 1
fi

# Test frontend
if curl -s http://localhost:3000 > /dev/null; then
    print_success "Frontend is running!"
else
    print_error "Frontend failed to start"
    pm2 logs touchline-frontend
    exit 1
fi

# Test Nginx
if curl -s http://$SERVER_IP > /dev/null; then
    print_success "Nginx proxy is working!"
else
    print_warning "Nginx proxy test failed, but services are running"
fi

echo ""
print_success "🎉 TouchLine deployed successfully!"
echo ""
echo "🌐 Application URLs:"
echo "   Frontend: http://$SERVER_IP:3000"
echo "   Backend API: http://$SERVER_IP:8000"
echo "   API Docs: http://$SERVER_IP:8000/docs"
echo "   Health Check: http://$SERVER_IP:8000/health/detailed"
echo ""
echo "📊 Management Commands:"
echo "   Check status: pm2 status"
echo "   View logs: pm2 logs"
echo "   Restart: pm2 restart touchline-backend touchline-frontend"
echo ""
print_warning "🔧 Next Steps:"
echo "1. Edit /var/www/touchline/backend/.env with your API keys"
echo "2. Edit /var/www/touchline/frontend/.env.local with your domain (if applicable)"
echo "3. Test SMS: cd /var/www/touchline/backend && source venv/bin/activate && python test_sms.py"
echo "4. Visit http://$SERVER_IP:3000 to use the application"
echo ""
print_info "📱 SMS Configuration:"
echo "   - Get Twilio credentials from https://console.twilio.com/"
echo "   - Get API-Football key from https://api-sports.io/"
echo "   - Update the .env file with your credentials"
echo ""
print_success "🚀 Your TouchLine application is now live!"
