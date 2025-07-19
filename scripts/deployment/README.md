# TouchLine Deployment Scripts

This directory contains all deployment and setup scripts for TouchLine.

## Scripts Overview

### Core Deployment
- **`deploy-simple.sh`** - Simple one-command deployment
- **`setup-app.sh`** - Application setup and configuration
- **`start-production.sh`** - Start production services

### Development & Testing
- **`setup-all.sh`** - Complete development environment setup
- **`start-all.sh`** - Start all development services

## Usage

### Production Deployment
```bash
# Simple deployment (run on DigitalOcean droplet)
./deploy-simple.sh

# Manual setup
./setup-app.sh
./start-production.sh
```

### Development Setup
```bash
# Complete development environment
./setup-all.sh
./start-all.sh
```

## Script Functions

### `deploy-simple.sh`
- Updates system packages
- Installs dependencies (Python, Node.js, PM2)
- Clones repository
- Sets up application
- Starts production services

### `setup-app.sh`
- Creates virtual environment
- Installs Python dependencies
- Sets up database
- Configures environment

### `start-production.sh`
- Starts FastAPI backend
- Starts Next.js frontend
- Configures PM2 process management
- Sets up monitoring

## Environment Requirements

- **Ubuntu 24.04 LTS** (recommended)
- **Git** access to repository
- **API keys** configured in `.env`
- **PM2** for process management

## Configuration

All scripts use environment variables from:
- `backend/.env` - Backend configuration
- `frontend/.env.local` - Frontend configuration 