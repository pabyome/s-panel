#!/bin/bash

# Update Script for s-panel
# This script pulls the latest changes, installs dependencies, builds the frontend, and restarts the service.

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                   s-panel Update                         ║"
echo "╚══════════════════════════════════════════════════════════╝"

# 1. Pull latest changes
echo "▶ Pulling latest changes from git..."
git pull origin main

# 2. Update Backend Dependencies
echo "▶ Updating backend dependencies..."
cd backend
if command -v uv &> /dev/null; then
    uv sync
else
    # Fallback if uv not found (though it should be)
    pip install .
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
# Assuming running under supervisor or systemd.
# If supervisor:
if command -v supervisorctl &> /dev/null; then
    supervisorctl restart spanel
    echo "✓ Service restarted via supervisor."
else
    # Fallback or systemd
    if systemctl is-active --quiet spanel; then
        sudo systemctl restart spanel
        echo "✓ Service restarted via systemd."
    else
        echo "⚠ Could not detect service manager. Please restart manually."
    fi
fi

echo "✓ Update complete!"
