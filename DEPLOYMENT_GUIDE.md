# 🚀 TouchLine DigitalOcean Deployment Guide

## Quick Deployment (One Command)

### Step 1: Create DigitalOcean Droplet
1. Go to: https://cloud.digitalocean.com/droplets/new
2. Choose:
   - **Image:** Ubuntu 24.04 LTS
   - **Size:** Basic $12/month (2GB RAM, 1 CPU, 50GB SSD)
   - **Region:** Choose closest to you
   - **Authentication:** SSH Key (recommended)
   - **Hostname:** `touchline-prod`
3. Click "Create Droplet"
4. Wait for it to finish (1-2 minutes)
5. Note the IP address (e.g., `157.245.123.456`)

### Step 2: Deploy TouchLine
Once you have your droplet IP, run this command:

```bash
# Replace YOUR_DROPLET_IP with your actual IP
ssh root@YOUR_DROPLET_IP "curl -fsSL https://raw.githubusercontent.com/czauhar/TouchLine/auto-dev/deploy-to-digitalocean.sh | bash"
```

**OR** connect manually and run the deployment:

```bash
# Connect to your droplet
ssh root@YOUR_DROPLET_IP

# Run the deployment script
curl -fsSL https://raw.githubusercontent.com/czauhar/TouchLine/auto-dev/deploy-to-digitalocean.sh | bash
```

### Step 3: Configure API Keys
After deployment, add your API keys:

```bash
# Edit the backend environment file
nano /var/www/touchline/backend/.env
```

**Add your actual API keys:**

```bash
# Twilio Configuration (for SMS alerts)
TWILIO_ACCOUNT_SID=your-actual-twilio-account-sid
TWILIO_AUTH_TOKEN=your-actual-twilio-auth-token
TWILIO_PHONE_NUMBER=your-actual-twilio-phone-number

# Sports API Configuration
API_FOOTBALL_KEY=your-actual-api-football-key
```

### Step 4: Restart the Application
```bash
# Restart the backend to load new environment variables
pm2 restart touchline-backend
```

## 🧪 Test SMS Functionality

### Test SMS Configuration
```bash
# Navigate to the backend directory
cd /var/www/touchline/backend

# Activate the virtual environment
source venv/bin/activate

# Test SMS configuration
python test_alert_messages.py
```

### Send a Test SMS
```bash
# Test SMS service
python test_sms.py
```

## 🌐 Access Your Application

- **Frontend:** `http://YOUR_DROPLET_IP:3000`
- **Backend API:** `http://YOUR_DROPLET_IP:8000`
- **API Documentation:** `http://YOUR_DROPLET_IP:8000/docs`
- **Health Check:** `http://YOUR_DROPLET_IP:8000/health/detailed`

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
curl http://localhost:8000/health/detailed
curl http://localhost:3000
```

## 📱 Create Your First Alert

1. **Visit the app:** Go to `http://YOUR_DROPLET_IP:3000`
2. **Sign up:** Create an account with your email
3. **Add phone number:** For SMS alerts
4. **Create alert:** Go to "Alerts" section
5. **Choose template:** Select from predefined templates
6. **Set phone number:** Add your phone number for SMS delivery

## 🎉 You're Done!

Your TouchLine application is now:
- ✅ **Deployed** on DigitalOcean
- ✅ **Running** with PM2 process management
- ✅ **SMS Ready** with Twilio integration
- ✅ **Monitoring** live matches
- ✅ **Processing** alerts in real-time

**Your sports alerting application is live and ready for users!** 🚀⚽📱
