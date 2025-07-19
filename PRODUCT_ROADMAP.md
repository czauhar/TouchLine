# TouchLine - Real-Time Sports SMS Alerts

## Product Vision
TouchLine is a **real-time sports alert system** that automatically sends SMS notifications when user-defined conditions are met during live matches. Users set thresholds (e.g., "Flamengo 2nd half ML is favorable") and receive instant alerts when those conditions trigger.

## Core Value Proposition
- **Set it and forget it**: Configure alerts once, get notified automatically
- **Real-time triggers**: SMS sent immediately when conditions are met
- **Personal use focus**: Simple, lightweight, no unnecessary features
- **Multi-sport ready**: Starting with soccer, expandable to other sports

## Tech Stack
- **Backend**: Python (FastAPI) - Fast, async, perfect for real-time data
- **Frontend**: Next.js with TypeScript - Clean interface for alert management
- **Database**: SQLite (development) / PostgreSQL (production) - Reliable data storage
- **SMS Service**: Twilio - Industry standard for SMS delivery
- **Sports Data**: API-Football (RapidAPI) - Comprehensive soccer data
- **Authentication**: JWT tokens - Secure user sessions

---

## Phase 1: Core SMS Alert System ✅ COMPLETE

### ✅ Backend Foundation
- [x] FastAPI server with async support
- [x] SQLite database with all tables
- [x] Sports API integration (API-Football)
- [x] Database models for Users, Matches, Alerts, AlertHistory
- [x] Real-time data fetching and storage

### ✅ Frontend Foundation  
- [x] Next.js app with TypeScript
- [x] Dashboard with system status
- [x] Matches page with live/today views
- [x] Responsive design with Tailwind CSS
- [x] Real-time data display

### ✅ Database & Data Flow
- [x] Match data syncing from sports API
- [x] Alert creation and management
- [x] User alert storage and retrieval
- [x] Data persistence and relationships

---

## Phase 2: SMS Integration & Alert Engine ✅ COMPLETE

### ✅ SMS Service Integration
- [x] Twilio API integration
- [x] SMS sending functionality
- [x] Message templating system
- [x] Delivery status tracking
- [x] Error handling and retries

### ✅ Real-Time Alert Engine
- [x] Background service for match monitoring (MatchMonitor)
- [x] Alert condition evaluation logic
- [x] Automatic SMS triggering
- [x] Alert history recording
- [x] Rate limiting and spam prevention

### ✅ Alert Types (Priority Order)
- [x] **Goal-based alerts**: "Team X scores 2+ goals"
- [x] **Score difference alerts**: "Team X leads by 2+ goals"  
- [x] **Time-based alerts**: "Team X scores in 2nd half"
- [x] **Advanced metrics alerts**: xG, momentum, pressure, win probability
- [x] **Custom statistical alerts**: Any API-available stat

### ✅ API Integration & Data
- [x] API-Football migration from RapidAPI to direct endpoint
- [x] Live match data fetching (63+ live matches)
- [x] Advanced metrics calculation (xG, momentum, pressure, win probability)
- [x] Real-time data processing and formatting
- [x] Database integration with proper error handling

---

## Phase 3: Advanced Condition Evaluator (Current Focus) 🚀

### Multi-Condition Alert Logic
- [ ] **AND/OR combinations**: "Team X scores AND has 60% possession"
- [ ] **Time-window conditions**: "Team X scores between 60-75 minutes"
- [ ] **Sequence conditions**: "Team X scores 2 goals within 10 minutes"
- [ ] **Pattern recognition**: "Team X scores in both halves"
- [ ] **Conditional chaining**: "If Team X scores first, then alert when they score again"

### Advanced Time-Based Logic
- [ ] **Period-specific alerts**: "Team X scores in first 15 minutes"
- [ ] **Half-time conditions**: "Team X leads at half-time"
- [ ] **End-game scenarios**: "Team X scores in last 10 minutes"
- [ ] **Overtime conditions**: "Team X scores in extra time"

### Enhanced Metrics Integration
- [ ] **Momentum-based alerts**: "Team X momentum > 15 for 5+ minutes"
- [ ] **Pressure index alerts**: "Team X pressure > 0.8 for 3+ minutes"
- [ ] **Win probability shifts**: "Team X win probability increases 20%"
- [ ] **xG accumulation**: "Team X xG > 2.0 by 60th minute"

### Smart Alert Management
- [ ] **Alert templates**: Pre-built common scenarios
- [ ] **Condition builder UI**: Visual condition creation
- [ ] **Alert testing**: Test conditions against historical data
- [ ] **Performance analytics**: Track alert success rates

---

## Phase 4: User Experience & Polish

### Alert Management Interface
- [ ] Create/edit/delete alerts
- [ ] Alert status dashboard
- [ ] Alert history and success tracking
- [ ] Alert templates for common scenarios
- [ ] Bulk alert operations

### User Authentication
- [ ] Simple user registration/login
- [ ] Phone number verification
- [ ] User profile management
- [ ] Alert ownership and privacy

### Real-Time Updates
- [ ] WebSocket connections for live updates
- [ ] Live match status on dashboard
- [ ] Alert trigger notifications in UI
- [ ] Real-time SMS delivery status

---

## Phase 4: Advanced Features

### Enhanced Alert Types
- [ ] **Multi-condition alerts**: "Team X scores AND has 60% possession"
- [ ] **Time-window alerts**: "Team X scores between 60-75 minutes"
- [ ] **League-specific alerts**: "Premier League matches only"
- [ ] **Odds-based alerts**: "When odds shift 20% in favor of Team X"

### Analytics & Insights
- [ ] Alert success rate tracking
- [ ] Most effective alert types
- [ ] Best performing teams/leagues
- [ ] Personal alert performance dashboard

### Performance Optimization
- [ ] Database query optimization
- [ ] API rate limiting and caching
- [ ] Background job scheduling
- [ ] Error recovery and resilience

---

## Phase 5: Production & Scaling

### Deployment & Infrastructure
- [ ] Production environment setup
- [ ] Database migration to PostgreSQL
- [ ] Environment configuration management
- [ ] Monitoring and logging
- [ ] Backup and recovery procedures

### Testing & Quality
- [ ] Unit tests for alert logic
- [ ] Integration tests for SMS delivery
- [ ] End-to-end alert flow testing
- [ ] Performance and load testing

### Security & Reliability
- [ ] Input validation and sanitization
- [ ] Rate limiting for SMS sending
- [ ] Error handling and fallbacks
- [ ] Security audit and hardening

---

## Success Metrics

### Core Functionality
- **SMS Delivery Rate**: > 95% successful delivery
- **Alert Accuracy**: > 90% correct trigger conditions
- **Response Time**: < 30 seconds from condition to SMS
- **System Uptime**: > 99% availability

### User Experience
- **Alert Creation**: < 2 minutes to set up new alert
- **Dashboard Load**: < 3 seconds page load time
- **Real-time Updates**: < 10 seconds data refresh
- **User Satisfaction**: Simple, reliable, effective

---

## Development Priorities

### Immediate (Next 1-2 weeks) ✅ COMPLETE
1. ✅ **Twilio SMS Integration** - Core functionality
2. ✅ **Alert Engine** - Background monitoring service
3. ✅ **Basic Alert Types** - Goal, score, possession alerts
4. ✅ **API Integration** - Live match data and advanced metrics

### Current Focus (Next 1-2 weeks) 🚀
1. **Multi-Condition Logic** - AND/OR combinations and complex conditions
2. **Advanced Time Windows** - Period-specific and sequence-based alerts
3. **Enhanced Metrics** - Momentum, pressure, and win probability conditions
4. **Condition Builder** - Visual interface for creating complex alerts

### Short Term (Next 2-4 weeks)
1. **Real-time Updates** - WebSocket integration
2. **Alert Management UI** - Create/edit/delete alerts
3. **Alert History** - Track success and performance
4. **User Authentication** - Simple login system

### Medium Term (Next 1-2 months)
1. **Analytics Dashboard** - Performance insights
2. **Advanced Alert Types** - Odds, time-windows, patterns
3. **Production Deployment** - Scalable infrastructure
4. **Testing & Polish** - Quality assurance

---

## Risk Mitigation

### Technical Risks
- **SMS Delivery Issues**: Implement retry logic and email fallback
- **API Rate Limits**: Cache data and optimize requests
- **Real-time Performance**: Use async processing and background jobs
- **Data Accuracy**: Validate and cross-reference sports data

### User Experience Risks
- **Alert Spam**: Implement rate limiting and user preferences
- **False Positives**: Fine-tune alert conditions and thresholds
- **Complex Setup**: Provide templates and guided setup
- **Mobile Experience**: Ensure responsive design works on phones

---

## Development Guidelines

### Code Quality
- **Python**: Follow PEP 8, use type hints, async/await patterns
- **TypeScript**: Strict typing, component-based architecture
- **Testing**: Unit tests for alert logic, integration tests for SMS
- **Documentation**: Clear API docs, setup instructions

### Performance
- **Database**: Optimize queries, use indexes, connection pooling
- **API**: Implement caching, rate limiting, async processing
- **Frontend**: Lazy loading, efficient re-renders, minimal bundle size
- **Real-time**: WebSocket connections, efficient data updates

### Security
- **Authentication**: JWT tokens, secure session management
- **Input Validation**: Sanitize all user inputs, prevent injection
- **SMS Security**: Rate limiting, user verification, audit logging
- **Data Privacy**: Encrypt sensitive data, user data ownership 