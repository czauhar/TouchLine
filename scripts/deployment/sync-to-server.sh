#!/bin/bash

# Sync TouchLine from local to server via git
# This ensures the server always matches the git repository

set -e

# Configuration
SERVER_USER="root"
SERVER_IP="64.225.56.165"
APP_DIR="/var/www/touchline"
REMOTE_BRANCH="${1:-auto-dev}"  # Default to auto-dev branch

echo "🔄 Syncing TouchLine to server..."
echo "📍 Server: $SERVER_USER@$SERVER_IP"
echo "📁 App Directory: $APP_DIR"
echo "🌿 Branch: $REMOTE_BRANCH"
echo ""

# Step 1: Commit local changes if any
echo "📝 Checking for uncommitted changes..."
cd "$(dirname "$0")/../.."

if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes locally"
    echo "   Files modified:"
    git status --short
    echo ""
    read -p "Commit these changes before syncing? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Committing changes..."
        git add -A
        git commit -m "Sync: Update server deployment $(date +%Y-%m-%d)"
    fi
fi

# Step 2: Push to remote
echo "📤 Pushing to remote repository..."
git push origin "$(git branch --show-current)"

# Step 3: Sync to server
echo "🔄 Syncing to server..."
ssh $SERVER_USER@$SERVER_IP << EOF
    set -e
    
    cd $APP_DIR
    
    # Check if it's a git repo
    if [ ! -d .git ]; then
        echo "❌ Not a git repository. Please initialize git first."
        exit 1
    fi
    
    # Fetch latest changes
    echo "📥 Fetching latest changes..."
    git fetch origin
    
    # Check current branch
    CURRENT_BRANCH=\$(git branch --show-current)
    echo "🌿 Current branch: \$CURRENT_BRANCH"
    
    # Switch to target branch if needed
    if [ "\$CURRENT_BRANCH" != "$REMOTE_BRANCH" ]; then
        echo "🔄 Switching to branch: $REMOTE_BRANCH"
        git checkout $REMOTE_BRANCH 2>/dev/null || git checkout -b $REMOTE_BRANCH origin/$REMOTE_BRANCH
    fi
    
    # Reset to match remote (discard local changes)
    echo "🔄 Resetting to match remote repository..."
    git reset --hard origin/$REMOTE_BRANCH
    
    # Update backend dependencies if needed
    echo "🐍 Checking backend dependencies..."
    cd backend
    if [ -d venv ]; then
        source venv/bin/activate
        pip install -q --upgrade -r requirements.txt || echo "⚠️  Some packages may have failed to install"
    else
        echo "⚠️  Backend venv not found, skipping dependency update"
    fi
    
    # Update frontend dependencies and rebuild
    echo "⚛️  Checking frontend dependencies..."
    cd ../frontend
    npm install --silent
    
    # Rebuild frontend
    echo "🏗️  Rebuilding frontend..."
    rm -rf .next
    npm run build
    
    echo "✅ Server files synced successfully!"
    echo "🔄 Restarting services..."
    cd ..
    pm2 restart touchline-backend touchline-frontend || echo "⚠️  PM2 restart failed, check pm2 status"
    
EOF

echo ""
echo "✅ Sync complete!"
echo "📊 Check server status with: ssh $SERVER_USER@$SERVER_IP 'pm2 status'"

