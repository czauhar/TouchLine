# 🚀 TouchLine Quick DigitalOcean Deployment

## ⚡ **One-Command Deployment**

### **Step 1: Create DigitalOcean Droplet**
1. Go to [DigitalOcean Control Panel](https://cloud.digitalocean.com/)
2. Create a new droplet:
   - **Image**: Ubuntu 24.04 LTS
   - **Size**: Basic $12/month (2GB RAM, 1 CPU)
   - **Region**: Choose closest to your users
   - **Authentication**: SSH Key (recommended)

### **Step 2: Deploy TouchLine**
Connect to your droplet and run this single command:

```bash
# Download and run the deployment script
curl -fsSL https://raw.githubusercontent.com/czauhar/TouchLine/auto-dev/deploy-to-digitalocean.sh | bash
```

**That's it!** Your TouchLine application will be deployed and running.

---

## 🔧 **After Deployment**

### **1. Configure API Keys**
Edit the environment file with your credentials:

```bash
nano /var/www/touchline/backend/.env
```

**Required API Keys:**
- **Twilio** (for SMS alerts): Get from [Twilio Console](https://console.twilio.com/)
- **API-Football** (for sports data): Get from [API-Sports](https://api-sports.io/)

### **2. Test SMS Notifications**
```bash
cd /var/www/touchline/backend
source venv/bin/activate
python test_sms.py
```

### **3. Access Your Application**
- **Frontend**: `http://YOUR_DROPLET_IP:3000`
- **Backend API**: `http://YOUR_DROPLET_IP:8000`
- **API Documentation**: `http://YOUR_DROPLET_IP:8000/docs`

---

## 📱 **Create Your First Alert**

1. **Visit the app**: Go to `http://YOUR_DROPLET_IP:3000`
2. **Sign up**: Create an account
3. **Add phone number**: For SMS alerts
4. **Create alert**: Choose from templates or create custom
5. **Test**: You'll receive SMS when conditions are met

---

## 🛠️ **Management Commands**

```bash
# Check application status
pm2 status

# View logs
pm2 logs

# Restart services
pm2 restart touchline-backend touchline-frontend

# Update application
cd /var/www/touchline
git pull origin auto-dev
pm2 restart touchline-backend touchline-frontend
```

---

## 🎉 **You're Done!**

Your TouchLine sports alerting application is now:
- ✅ **Deployed** on DigitalOcean
- ✅ **Running** with PM2 process management
- ✅ **Ready** for SMS notifications
- ✅ **Monitoring** live matches
- ✅ **Processing** alerts in real-time

**Your sports alerting application is live and ready for users!** 🚀⚽📱
