#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== s-panel Server Installer ===${NC}"

# Check for root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (sudo ./install.sh)${NC}"
    exit
fi

# 1. Update and Install System Dependencies
echo -e "${GREEN}[1/5] Installing System Dependencies...${NC}"
apt update
apt install -y python3 python3-venv git unzip curl gnupg ufw supervisor nginx

# 2. Install Node.js 20.x
if ! command -v node &> /dev/null; then
    echo -e "${GREEN}[2/5] Installing Node.js 20...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
else
    echo -e "${GREEN}[2/5] Node.js already installed.${NC}"
fi

# 3. Install uv (Python Package Manager)
if ! command -v uv &> /dev/null; then
    echo -e "${GREEN}[3/5] Installing 'uv'...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
else
    echo -e "${GREEN}[3/5] 'uv' already installed.${NC}"
fi

# 4. Build Frontend
echo -e "${GREEN}[4/5] Building Frontend...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run build
cd ..

# 5. Backend Setup
echo -e "${GREEN}[5/5] Setting up Backend...${NC}"
cd backend

# Create missing .env if needed
if [ ! -f .env ]; then
    echo "Creating .env file with generated secret..."
    RANDOM_KEY=$(openssl rand -hex 32)
    echo "SECRET_KEY=$RANDOM_KEY" > .env
    echo "ALGORITHM=HS256" >> .env
    echo "ACCESS_TOKEN_EXPIRE_MINUTES=10080" >> .env
    echo "BACKEND_CORS_ORIGINS=[\"http://localhost:5173\"]" >> .env
fi

# Install dependencies
uv sync

# Generate Service File automatically for THIS server
# We use the python script but non-interactive via input redirection or slight modification
# Actually, let's just run it interactively if the user wants?
# Or simpler: The user should have run it locally or runs it now.

if [ ! -f "spanel.service" ]; then
    echo -e "${RED}Warning: 'spanel.service' not found in backend/.${NC}"
    echo "Running generator now... Please select 'y' for current machine."
    python3 generate_service.py
fi

if [ -f "spanel.service" ]; then
    echo "Installing Service..."
    cp spanel.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable --now spanel
    echo -e "${GREEN}Service Installed & Started!${NC}"
    systemctl status spanel --no-pager
else
    echo -e "${RED}Service file not created. Please run 'python3 generate_service.py' manually.${NC}"
fi

echo -e "${GREEN}=== Installation Complete! ===${NC}"
echo "Your s-panel should be running on port 8000."
echo "Configure Nginx to proxy 80/443 to localhost:8000."
