# 🚀 TouchLine Simple Deployment

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

## Updates

```bash
cd /var/www/touchline
git pull origin main
pm2 restart all
``` 