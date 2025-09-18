# 🚀 Deploy TouchLine to 68.183.59.147

## Option 1: Manual Deployment (Recommended)

Since the server isn't responding to SSH, you'll need to access it through the DigitalOcean console or fix the SSH connection first.

### Step 1: Access Your Server
1. **Go to DigitalOcean Console:** https://cloud.digitalocean.com/droplets
2. **Click on your droplet** (68.183.59.147)
3. **Click "Console"** to access the server directly
4. **Login as root** (or your user account)

### Step 2: Run the Deployment Script
Once you're in the server console, run:

```bash
# Download and run the deployment script
curl -fsSL https://raw.githubusercontent.com/czauhar/TouchLine/auto-dev/deploy-to-digitalocean.sh | bash
```

**OR** if that doesn't work, run this step by step:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx git curl certbot python3-certbot-nginx

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2
sudo npm install -g pm2

# Clone the app
cd /var/www
sudo rm -rf touchline
sudo git clone https://github.com/czauhar/TouchLine.git touchline
sudo chown -R $USER:$USER touchline
cd touchline

# Setup the app
chmod +x scripts/deployment/setup-app.sh scripts/deployment/start-production.sh
./scripts/deployment/setup-app.sh
```

### Step 3: Configure Nginx
```bash
# Create Nginx configuration
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

# Enable the site
sudo ln -sf /etc/nginx/sites-available/touchline /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Step 4: Start the Application
```bash
# Start the application
cd /var/www/touchline
./scripts/deployment/start-production.sh
```

### Step 5: Configure API Keys
```bash
# Edit the backend environment file
nano /var/www/touchline/backend/.env
```

**Add your API keys:**
```bash
# Database Configuration
DATABASE_URL=sqlite:///./touchline.db

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Twilio Configuration (for SMS alerts)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# Sports API Configuration
API_FOOTBALL_KEY=your-api-football-key
SPORTS_API_BASE_URL=https://v3.football.api-sports.io/

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Monitoring Configuration
MONITORING_INTERVAL=60
MAX_RETRIES=3

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,https://touchline.app,https://www.touchline.app
```

### Step 6: Restart and Test
```bash
# Restart the application
pm2 restart touchline-backend

# Test the deployment
curl http://localhost:8000/health/detailed
curl http://localhost:3000
```

## Option 2: Fix SSH Connection

If you want to use SSH instead of the console:

### Check SSH Configuration
```bash
# On your local machine, check if SSH is working
ssh -v root@68.183.59.147

# If it's a key issue, try:
ssh -i ~/.ssh/id_rsa root@68.183.59.147

# Or if you have a specific key:
ssh -i /path/to/your/key root@68.183.59.147
```

### Check Firewall Settings
```bash
# On the server (via console), check firewall:
sudo ufw status
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 3000
sudo ufw allow 8000
```

## 🧪 Test Your Deployment

Once deployed, test these endpoints:

```bash
# Test backend health
curl http://68.183.59.147:8000/health/detailed

# Test frontend
curl http://68.183.59.147:3000

# Test SMS service (on the server)
cd /var/www/touchline/backend
source venv/bin/activate
python test_alert_messages.py
```

## 📱 Access Your Live App

- **Frontend:** http://68.183.59.147:3000
- **Backend API:** http://68.183.59.147:8000
- **Health Check:** http://68.183.59.147:8000/health/detailed

## 🔧 Troubleshooting

### Check Application Status
```bash
# Check if services are running
pm2 status

# View logs
pm2 logs
```

### Restart Services
```bash
# Restart all services
pm2 restart touchline-backend touchline-frontend
```

### Check Ports
```bash
# Check if ports are accessible
netstat -tlnp | grep :8000
netstat -tlnp | grep :3000
```

## 🎉 You're Done!

Your TouchLine application will be live at:
- **Frontend:** http://68.183.59.147:3000
- **Backend:** http://68.183.59.147:8000

**Your sports alerting application is ready to send real SMS alerts!** 🚀⚽📱
