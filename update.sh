#!/bin/bash

# Update Script for s-panel
# This script pulls the latest changes, installs dependencies, builds the frontend, and restarts the service.

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                   s-panel Update                         ║"
echo "╚══════════════════════════════════════════════════════════╝"

# 0. Check for Local Docker Registry
if command -v docker &> /dev/null; then
    if ! docker ps --format '{{.Names}}' | grep -q "^registry$"; then
        echo "▶ Starting local Docker registry..."
        # Remove if it exists but stopped
        docker rm -f registry 2>/dev/null || true
        # Start new registry
        docker run -d -p 5001:5000 --restart=always --name registry registry:2
    fi
fi

# 1. Pull latest changes
echo "▶ Pulling latest changes from git..."
# Fix for "dubious ownership" if running as root in user-owned dir
git config --global --add safe.directory $(pwd)
git pull origin main

# 2. Update Backend Dependencies
echo "▶ Updating backend dependencies..."
cd backend
if command -v uv &> /dev/null; then
    uv sync
else
    echo "❌ 'uv' is not installed. Please install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 2b. Run Database Migrations
echo "▶ Running database migrations..."
if [ -f "run_migrations.py" ]; then
    python3 run_migrations.py
else
    echo "  ℹ No migration runner found"
fi

cd ..

# 3. Update Frontend Dependencies and Build
echo "▶ Updating frontend..."
cd frontend
if [ -f "yarn.lock" ]; then
    yarn install
    yarn build
else
    npm install
    npm run build
fi
cd ..

# 4. Restart Service
echo "▶ Restarting s-panel service..."

if command -v systemctl &> /dev/null && systemctl cat spanel.service &> /dev/null; then
    sudo systemctl restart spanel
    echo "✓ Service restarted via systemd."
elif command -v supervisorctl &> /dev/null && supervisorctl status spanel &> /dev/null; then
    supervisorctl restart spanel
    echo "✓ Service restarted via supervisor."
else
    echo "⚠ Could not detect 'spanel' service in systemd or supervisor."
    echo "⚠ Please restart the service manually."
fi

echo "✓ Update complete!"
