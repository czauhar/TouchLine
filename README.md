# TouchLine - Live Sports Stats Alerting Application

A modern full-stack application for real-time sports statistics monitoring and alerting.

> **🚀 Recently Refactored**: The application has been completely refactored with improved organization, PostgreSQL-only database, and a comprehensive component library. See [REFACTOR_PROGRESS.md](./REFACTOR_PROGRESS.md) for details.

## 🏗️ Architecture

```
TouchLine/
├── 🐍 backend/          # FastAPI Python backend (PostgreSQL)
├── ⚛️ frontend/         # Next.js React frontend with component library
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

- **Backend**: FastAPI, Python, SQLAlchemy, PostgreSQL
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Component Library**: Custom UI components with Radix-like patterns
- **Authentication**: NextAuth.js
- **SMS**: Twilio
- **Sports Data**: API-Football
- **Caching**: Redis
- **Deployment**: PM2, Nginx, Docker, DigitalOcean

## 📁 Project Structure

### Backend (`/backend/`)
- `main.py` - FastAPI application entry point
- `app/` - Core application modules
  - `routers/` - API endpoints (REST)
  - `services/` - Business logic (static method pattern)
  - `models.py` - SQLAlchemy database models
  - `core/` - Configuration and exceptions
  - `utils/` - Validation and logging utilities
  - `auth.py` - JWT authentication
  - `sms_service.py` - Twilio SMS integration

### Frontend (`/frontend/`)
- `app/` - Next.js 14 App Router pages
- `components/` - Reusable UI components
  - `ui/` - Base components (Button, Card, Input, etc.)
  - `matches/` - Match-related components
  - `alerts/` - Alert management components
  - `dashboard/` - Dashboard widgets
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
