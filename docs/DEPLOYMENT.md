# 🚀 TouchLine Simple Deployment

## Development Workflow

### Local Development
- **Your local machine** for development and testing
- Fast iteration, debugging, and feature development
- No risk of breaking production

### Production Pipeline
- **GitHub** → **DigitalOcean droplet** (auto-deploy)
- When you push to `main` branch, it updates production
- Clean, stable Ubuntu 24.04 LTS environment

### Workflow
1. **Develop locally** → test changes
2. **Push to GitHub** → triggers production update
3. **SSH to droplet** → update and restart (or automated)

## Quick Deploy

SSH into your DigitalOcean droplet and run:

```bash
# One command deployment
curl -sSL https://raw.githubusercontent.com/czauhar/TouchLine/main/deploy-simple.sh | bash
```

## Manual Deploy

```bash
# Clone and setup
cd /var/www
git clone https://github.com/czauhar/TouchLine.git touchline
cd touchline
chmod +x deploy-simple.sh
./deploy-simple.sh
```

## What It Does

✅ Installs Python, Node.js, PM2  
✅ Clones your app from GitHub  
✅ Sets up backend and frontend  
✅ Starts both servers  
✅ Configures PM2 for auto-restart  

## After Deployment

- **Backend**: `http://your-server-ip:8000`
- **Frontend**: `http://your-server-ip:3000`
- **Status**: `pm2 status`

## Optional: Add API Keys

Edit `backend/.env` to add:
```env
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_number
RAPIDAPI_KEY=your_key
```

## Production Updates

### Quick Update
```bash
# SSH to droplet
ssh root@your-droplet-ip

# Update and restart
cd /var/www/touchline
git pull origin main
pm2 restart all
```

### Check Status
```bash
pm2 status
pm2 logs
```

## System Requirements

- **Ubuntu 24.04 LTS** (recommended) or Ubuntu 22.04 LTS
- **1 vCPU, 1GB RAM** minimum (DigitalOcean droplet)
- **Git** access to repository 