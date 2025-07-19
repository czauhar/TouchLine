# TouchLine Configuration Files

This directory contains configuration files for deployment and infrastructure.

## Configuration Files

### Process Management
- **`ecosystem.config.js`** - PM2 process configuration
  - Backend FastAPI service
  - Frontend Next.js service
  - Environment variables
  - Auto-restart settings

### Web Server
- **`nginx-touchline.conf`** - Nginx configuration
  - Reverse proxy setup
  - SSL configuration
  - Static file serving
  - Load balancing

## Usage

### PM2 Configuration
```bash
# Start services with PM2
pm2 start ecosystem.config.js

# Monitor services
pm2 status
pm2 logs
```

### Nginx Configuration
```bash
# Copy to nginx sites-available
sudo cp nginx-touchline.conf /etc/nginx/sites-available/touchline

# Enable site
sudo ln -s /etc/nginx/sites-available/touchline /etc/nginx/sites-enabled/

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

## Configuration Details

### Ecosystem Config
- **Backend**: FastAPI on port 8000
- **Frontend**: Next.js on port 3000
- **Environment**: Production settings
- **Monitoring**: PM2 monitoring enabled

### Nginx Config
- **Domain**: Configured for touchline.com
- **SSL**: Let's Encrypt certificate setup
- **Proxy**: Routes API calls to backend
- **Static**: Serves frontend build files

## Environment Variables

Configuration files reference these environment variables:
- `DATABASE_URL` - Database connection string
- `API_FOOTBALL_KEY` - Sports API key
- `TWILIO_*` - SMS service credentials 