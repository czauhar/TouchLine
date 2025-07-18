# TouchLine - Real-Time Sports SMS Alerts

TouchLine is a **real-time sports alert system** that automatically sends SMS notifications when user-defined conditions are met during live matches. Users set thresholds (e.g., "Flamengo 2nd half ML is favorable") and receive instant alerts when those conditions trigger.

## 🎯 Core Value Proposition
- **Set it and forget it**: Configure alerts once, get notified automatically
- **Real-time triggers**: SMS sent immediately when conditions are met  
- **Personal use focus**: Simple, lightweight, no unnecessary features
- **Multi-sport ready**: Starting with soccer, expandable to other sports

## 🏗️ Architecture

- **Backend**: Python FastAPI
- **Frontend**: Next.js with TypeScript
- **Database**: PostgreSQL (with SQLite fallback for development)
- **SMS**: Twilio API
- **Sports Data**: API-Football (RapidAPI)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- PostgreSQL (optional, SQLite used by default)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run the backend:**
   ```bash
   python main.py
   ```
   
   Backend will be available at: http://localhost:8000

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the frontend:**
   ```bash
   npm run dev
   ```
   
   Frontend will be available at: http://localhost:3000

## 📁 Project Structure

```
TouchLine/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py          # Database models
│   │   └── database.py        # Database configuration
│   ├── main.py               # FastAPI application
│   ├── requirements.txt      # Python dependencies
│   └── env.example          # Environment variables template
├── frontend/
│   ├── app/
│   │   ├── layout.tsx        # Root layout
│   │   ├── page.tsx          # Main page
│   │   └── globals.css       # Global styles
│   ├── package.json          # Node.js dependencies
│   ├── next.config.js        # Next.js configuration
│   └── tsconfig.json         # TypeScript configuration
├── PRODUCT_ROADMAP.md        # Development roadmap
└── README.md                 # This file
```

## 🔧 Configuration

### Environment Variables (Backend)

Copy `backend/env.example` to `backend/.env` and configure:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `TWILIO_ACCOUNT_SID`: Twilio account SID
- `TWILIO_AUTH_TOKEN`: Twilio auth token
- `TWILIO_PHONE_NUMBER`: Twilio phone number
- `SPORTS_API_KEY`: Sports API key

## 📊 Current Status

### ✅ Completed (Phase 1)
- [x] FastAPI backend with async support
- [x] SQLite database with all tables
- [x] Sports API integration (API-Football)
- [x] Database models for Users, Matches, Alerts, AlertHistory
- [x] Next.js frontend with TypeScript
- [x] Dashboard with system status
- [x] Matches page with live/today views
- [x] Alert creation and management API
- [x] Real-time data fetching and storage

### 🚧 Current Focus (Phase 2)
- [ ] **Twilio SMS Integration** - Core functionality
- [ ] **Alert Engine** - Background monitoring service
- [ ] **Basic Alert Types** - Goal, score, possession alerts
- [ ] **User Authentication** - Simple login system

### 📋 Next Steps
- [ ] Real-time updates with WebSockets
- [ ] Alert management UI
- [ ] Alert history and success tracking
- [ ] Enhanced alert types (multi-condition, time-windows)

## 🛠️ Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python main.py
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### API Documentation
Once the backend is running, visit: http://localhost:8000/docs

## 📝 Notes

- The application uses SQLite by default for development
- CORS is configured for localhost:3000 (frontend)
- All dependencies are kept minimal for lightweight deployment
- The project follows a modular structure for easy scaling

## 🤝 Contributing

1. Follow the roadmap in `PRODUCT_ROADMAP.md`
2. Keep the application lightweight
3. Use TypeScript for frontend
4. Follow PEP 8 for Python code
5. Test thoroughly before committing 