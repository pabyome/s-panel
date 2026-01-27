#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== s-panel Update Script ===${NC}"

# 1. Pull Latest Code
echo -e "${GREEN}[1/4] Pulling latest code...${NC}"
git pull

# 2. Update Backend Dependencies
echo -e "${GREEN}[2/4] Updating Backend...${NC}"
cd backend
uv sync
cd ..

# 3. Rebuild Frontend
echo -e "${GREEN}[3/4] Rebuilding Frontend...${NC}"
cd frontend
npm install
npm run build
cd ..

# 4. Restart Service
echo -e "${GREEN}[4/4] Restarting Service...${NC}"
if systemctl is-active --quiet spanel; then
    sudo systemctl restart spanel
    echo "Service restarted."
else
    echo "Service 'spanel' is not running. Attempting to start..."
    sudo systemctl start spanel
fi

sudo systemctl status spanel --no-pager

echo -e "${GREEN}=== Update Complete! ===${NC}"
