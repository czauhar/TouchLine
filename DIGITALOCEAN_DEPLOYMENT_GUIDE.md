# 🚀 TouchLine DigitalOcean Deployment Guide

## 📋 **Prerequisites**

Before deploying, you'll need:
- ✅ DigitalOcean account
- ✅ Domain name (optional, but recommended)
- ✅ API keys (Twilio, API-Football)
- ✅ SSH access to your droplet

---

## 🎯 **Step 1: Create DigitalOcean Droplet**

### **Recommended Droplet Configuration:**
- **Size**: Basic Droplet - $12/month (2GB RAM, 1 CPU, 50GB SSD)
- **Image**: Ubuntu 24.04 LTS
- **Region**: Choose closest to your users
- **Authentication**: SSH Key (recommended) or Password

### **Create Droplet:**
1. Go to [DigitalOcean Control Panel](https://cloud.digitalocean.com/)
2. Click "Create" → "Droplets"
3. Choose Ubuntu 24.04 LTS
4. Select Basic plan ($12/month)
5. Add your SSH key
6. Choose a hostname (e.g., `touchline-prod`)
7. Click "Create Droplet"

---

## 🔧 **Step 2: Initial Server Setup**

### **Connect to your droplet:**
```bash
ssh root@YOUR_DROPLET_IP
```

### **Update system:**
```bash
apt update && apt upgrade -y
```

### **Create non-root user (recommended):**
```bash
adduser touchline
usermod -aG sudo touchline
su - touchline
```

---

## 🚀 **Step 3: Deploy TouchLine**

### **Option A: Automated Deployment (Recommended)**

Run this single command on your droplet:

```bash
# Download and run the deployment script
curl -fsSL https://raw.githubusercontent.com/czauhar/TouchLine/auto-dev/scripts/deployment/deploy-digitalocean.sh | bash
```

### **Option B: Manual Deployment**

If you prefer manual control:

```bash
# Clone the repository
cd /var/www
git clone https://github.com/czauhar/TouchLine.git touchline
cd touchline

# Make scripts executable
chmod +x scripts/deployment/*.sh

# Run deployment
./scripts/deployment/deploy-digitalocean.sh
```

---

## ⚙️ **Step 4: Configure Environment Variables**

### **Backend Configuration:**
```bash
nano /var/www/touchline/backend/.env
```

**Required Configuration:**
```bash
# Database Configuration
DATABASE_URL=sqlite:///./touchline.db

# JWT Configuration
SECRET_KEY=your-production-secret-key-change-this
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
DEBUG=False
```

### **Frontend Configuration:**
```bash
nano /var/www/touchline/frontend/.env.local
```

**Required Configuration:**
```bash
NEXT_PUBLIC_API_URL=http://YOUR_DROPLET_IP:8000
NEXTAUTH_SECRET=your-production-nextauth-secret
NEXTAUTH_URL=http://YOUR_DROPLET_IP:3000
```

---

## 🌐 **Step 5: Configure Domain (Optional)**

### **If you have a domain:**

1. **Update DNS:**
   - Point your domain to your droplet IP
   - Add A record: `@` → `YOUR_DROPLET_IP`
   - Add A record: `www` → `YOUR_DROPLET_IP`

2. **Update Nginx configuration:**
   ```bash
   nano /etc/nginx/sites-available/touchline
   ```
   
   Replace `your-domain.com` with your actual domain:
   ```nginx
   server_name your-domain.com www.your-domain.com;
   ```

3. **Update frontend environment:**
   ```bash
   nano /var/www/touchline/frontend/.env.local
   ```
   ```bash
   NEXT_PUBLIC_API_URL=http://your-domain.com:8000
   NEXTAUTH_URL=http://your-domain.com:3000
   ```

---

## 🔒 **Step 6: Setup SSL Certificate (Optional)**

### **Install SSL with Let's Encrypt:**
```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
certbot renew --dry-run
```

---

## 🚀 **Step 7: Start the Application**

### **Start production services:**
```bash
cd /var/www/touchline
./scripts/deployment/start-production.sh
```

### **Check status:**
```bash
pm2 status
pm2 logs
```

---

## 📊 **Step 8: Verify Deployment**

### **Test your deployment:**

1. **Backend Health Check:**
   ```bash
   curl http://YOUR_DROPLET_IP:8000/health/detailed
   ```

2. **Frontend Access:**
   - Visit: `http://YOUR_DROPLET_IP:3000`
   - Or: `http://your-domain.com:3000` (if domain configured)

3. **API Documentation:**
   - Visit: `http://YOUR_DROPLET_IP:8000/docs`

---

## 🔧 **Step 9: Configure SMS Testing**

### **Test SMS functionality:**
```bash
cd /var/www/touchline/backend
source venv/bin/activate
python test_sms.py
```

### **Test alert message formatting:**
```bash
python test_alert_messages.py
```

---

## 📱 **Step 10: Create Your First Alert**

1. **Visit the application:**
   - Go to `http://YOUR_DROPLET_IP:3000`
   - Sign up for an account
   - Add your phone number

2. **Create an alert:**
   - Go to "Alerts" section
   - Choose from templates or create custom
   - Set your phone number for SMS delivery

3. **Test the alert:**
   - The system will monitor live matches
   - You'll receive SMS when conditions are met

---

## 🛠️ **Management Commands**

### **Application Management:**
```bash
# Check status
pm2 status

# View logs
pm2 logs

# Restart services
pm2 restart touchline-backend touchline-frontend

# Stop services
pm2 stop touchline-backend touchline-frontend

# Start services
pm2 start touchline-backend touchline-frontend
```

### **Update Application:**
```bash
cd /var/www/touchline
git pull origin auto-dev
pm2 restart touchline-backend touchline-frontend
```

### **View System Logs:**
```bash
# Application logs
pm2 logs

# System logs
journalctl -u nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **Port 8000/3000 not accessible:**
   ```bash
   # Check if services are running
   pm2 status
   
   # Check firewall
   ufw status
   ufw allow 8000
   ufw allow 3000
   ```

2. **Database issues:**
   ```bash
   cd /var/www/touchline/backend
   source venv/bin/activate
   python migrate_database.py
   ```

3. **SMS not working:**
   - Check Twilio credentials in `.env`
   - Test with `python test_sms.py`

4. **Frontend not loading:**
   - Check if backend is running
   - Verify API URL in frontend `.env.local`

---

## 📊 **Monitoring & Maintenance**

### **Health Monitoring:**
- **Backend Health**: `http://YOUR_DROPLET_IP:8000/health/detailed`
- **System Status**: `pm2 status`
- **Logs**: `pm2 logs`

### **Regular Maintenance:**
```bash
# Update system packages
apt update && apt upgrade -y

# Update application
cd /var/www/touchline
git pull origin auto-dev
pm2 restart touchline-backend touchline-frontend

# Clean up logs
pm2 flush
```

---

## 🎉 **Deployment Complete!**

Your TouchLine application is now running on DigitalOcean with:

- ✅ **Backend**: FastAPI on port 8000
- ✅ **Frontend**: Next.js on port 3000
- ✅ **Database**: SQLite with optimized connection pooling
- ✅ **SMS Service**: Twilio integration ready
- ✅ **Alert Engine**: Real-time pattern recognition
- ✅ **Health Monitoring**: Comprehensive system monitoring
- ✅ **SSL Support**: Ready for domain configuration
- ✅ **Process Management**: PM2 for production stability

**Your sports alerting application is now live and ready for users!** 🚀⚽📱
