# TouchLine - Live Sports Stats Alerting Application

A modern full-stack application for real-time sports statistics monitoring and alerting.

## 🏗️ Architecture

```
TouchLine/
├── 🐍 backend/          # FastAPI Python backend
├── ⚛️ frontend/         # Next.js React frontend  
├── 📜 scripts/         # Deployment & automation
├── ⚙️ config/          # Configuration files
└── 🐳 docker-compose.yml
```

## 🚀 Quick Start

### Development Setup

1. **Backend Setup:**
   ```bash
   cd backend
   source venv/bin/activate
   python main.py
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access Application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🎯 Features

- **Live Match Monitoring**: Real-time sports data ingestion
- **Custom Alerts**: User-defined alert rules and conditions
- **SMS Notifications**: Twilio integration for instant alerts
- **Dashboard**: Real-time system health and statistics
- **User Management**: Authentication and profile management

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python, SQLAlchemy, SQLite
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Authentication**: NextAuth.js
- **SMS**: Twilio
- **Sports Data**: API-Football
- **Deployment**: PM2, Nginx, Docker

## 📁 Project Structure

### Backend (`/backend/`)
- `main.py` - FastAPI application entry point
- `app/` - Core application modules
  - `routers/` - API endpoints
  - `services/` - Business logic
  - `models.py` - Database models
  - `auth.py` - Authentication
  - `sms_service.py` - SMS notifications

### Frontend (`/frontend/`)
- `app/` - Next.js pages and API routes
- `components/` - Reusable UI components
- `lib/` - Utility functions and API client

### Scripts (`/scripts/`)
- `deployment/` - Production deployment scripts
- `dev-setup.sh` - Development environment setup

## 🔧 Configuration

Environment variables are configured in:
- `backend/.env` - Backend configuration
- `frontend/.env.local` - Frontend configuration

## 🚀 Deployment

Use the deployment scripts in `/scripts/deployment/` for production deployment.

## 📊 Status

The application is fully functional with:
- ✅ Live sports data ingestion
- ✅ Custom alert system
- ✅ SMS notifications
- ✅ Real-time dashboard
- ✅ User authentication
- ✅ Production deployment ready
