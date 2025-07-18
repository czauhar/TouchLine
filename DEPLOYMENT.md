# 🚀 TouchLine DigitalOcean Deployment Guide

## Prerequisites
- DigitalOcean droplet (Ubuntu 22.04 recommended)
- Domain name (optional but recommended)
- Twilio account for SMS
- API-Football account for sports data

## 📋 Step-by-Step Deployment

### 1. Initial Server Setup

SSH into your DigitalOcean droplet and run:

```bash
# Download and run the deployment script
curl -O https://raw.githubusercontent.com/yourusername/touchline/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### 2. Copy TouchLine Files

Option A: Using Git (recommended)
```bash
cd /var/www/touchline
git clone https://github.com/yourusername/touchline.git .
```

Option B: Using SCP/SFTP
```bash
# From your local machine
scp -r /path/to/touchline/* root@your-server-ip:/var/www/touchline/
```

### 3. Setup Application

```bash
cd /var/www/touchline
chmod +x setup-app.sh
./setup-app.sh
```

### 4. Configure Environment Variables

Edit the backend environment file:
```bash
nano /var/www/touchline/backend/.env
```

Add your API credentials:
```env
# Twilio SMS
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here

# Sports API
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=api-football-v1.p.rapidapi.com
```

### 5. Configure Nginx

```bash
# Copy Nginx configuration
sudo cp nginx-touchline.conf /etc/nginx/sites-available/touchline

# Edit the configuration with your domain
sudo nano /etc/nginx/sites-available/touchline

# Enable the site
sudo ln -s /etc/nginx/sites-available/touchline /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 6. Setup SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 7. Start Application

```bash
cd /var/www/touchline
chmod +x start-production.sh
./start-production.sh
```

### 8. Create Log Directory

```bash
sudo mkdir -p /var/log/touchline
sudo chown $USER:$USER /var/log/touchline
```

## 🔧 Management Commands

### PM2 Commands
```bash
# Check status
pm2 status

# View logs
pm2 logs touchline-backend
pm2 logs touchline-frontend

# Restart services
pm2 restart touchline-backend
pm2 restart touchline-frontend

# Stop services
pm2 stop touchline-backend touchline-frontend

# Start services
pm2 start touchline-backend touchline-frontend
```

### Nginx Commands
```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

### Database Management
```bash
# Access SQLite database
cd /var/www/touchline/backend
sqlite3 touchline.db

# Backup database
cp touchline.db touchline.db.backup.$(date +%Y%m%d_%H%M%S)
```

## 📊 Monitoring

### Check Application Status
```bash
# Backend health
curl http://localhost:8000/health

# API status
curl http://localhost:8000/api/status

# Frontend
curl http://localhost:3000
```

### Monitor Logs
```bash
# Real-time logs
tail -f /var/log/touchline/backend-out.log
tail -f /var/log/nginx/touchline_access.log

# Error logs
tail -f /var/log/touchline/backend-error.log
tail -f /var/log/nginx/touchline_error.log
```

## 🔄 Updates

### Update Application
```bash
cd /var/www/touchline

# Pull latest changes
git pull origin main

# Update dependencies
cd backend && source venv/bin/activate && pip install -r requirements.txt
cd ../frontend && npm install && npm run build

# Restart services
pm2 restart all
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   sudo netstat -tulpn | grep :8000
   sudo kill -9 <PID>
   ```

2. **Permission denied**
   ```bash
   sudo chown -R $USER:$USER /var/www/touchline
   ```

3. **Nginx 502 error**
   ```bash
   # Check if backend is running
   pm2 status
   # Check backend logs
   pm2 logs touchline-backend
   ```

4. **SSL certificate issues**
   ```bash
   sudo certbot renew --dry-run
   ```

## 📈 Scaling

### Upgrade Droplet
- Go to DigitalOcean dashboard
- Power off droplet
- Resize droplet
- Power on droplet

### Add Load Balancer
- Create DigitalOcean load balancer
- Add multiple droplets
- Configure health checks

## 💰 Cost Optimization

### Current Costs (Monthly)
- **Droplet**: $5-10
- **Domain**: $1-2
- **SMS (Twilio)**: $1-20 (depending on usage)
- **Sports API**: $10-30
- **Total**: $17-62/month

### Optimization Tips
- Use free tier of sports API initially
- Monitor SMS usage and set limits
- Cache API responses
- Use SQLite instead of PostgreSQL for small scale

## 🆘 Support

If you encounter issues:
1. Check logs: `pm2 logs` and `sudo journalctl -u nginx`
2. Verify configuration files
3. Test endpoints individually
4. Check DigitalOcean status page 