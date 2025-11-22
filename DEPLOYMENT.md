# Deployment Guide

## Quick Sync to Server

To sync your local changes to the server (ensures they match):

```bash
./scripts/deployment/sync-to-server.sh
```

Or specify a branch:
```bash
./scripts/deployment/sync-to-server.sh main
```

## Manual Deployment Steps

If you prefer to deploy manually:

1. **Commit your changes locally:**
   ```bash
   git add -A
   git commit -m "Your commit message"
   git push origin <your-branch>
   ```

2. **SSH to server and pull:**
   ```bash
   ssh root@64.225.56.165
   cd /var/www/touchline
   git fetch origin
   git checkout <branch>
   git reset --hard origin/<branch>
   ```

3. **Update dependencies:**
   ```bash
   # Backend
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   npm run build
   ```

4. **Restart services:**
   ```bash
   cd ..
   pm2 restart touchline-backend touchline-frontend
   ```

## Current Server Status

- **Location:** `/var/www/touchline`
- **Git Branch:** `main` (has diverged from local)
- **Backend:** Running via PM2 on port 8000
- **Frontend:** Running via PM2 on port 3000

## Important Notes

- Always commit changes before syncing
- The server has a `.env` file with production credentials - don't overwrite it
- Frontend `.env.local` contains `NEXT_PUBLIC_API_URL` - preserve this
- Backend uses PostgreSQL, not SQLite (despite what some configs might say)

