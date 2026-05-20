#!/bin/bash

# Usage: bash start.sh  (run from the WashSaleApp directory)

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "=== Wash Sale Checker ==="
echo ""

# ── 1. Prerequisites ─────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}Error: python3 not found. Install from https://www.python.org/downloads/${NC}"
    exit 1
fi
if ! command -v node &>/dev/null; then
    echo -e "${RED}Error: node not found. Install from https://nodejs.org/${NC}"
    exit 1
fi

# ── 2. Config ─────────────────────────────────────────────────────────────────
if [ ! -f config.yaml ]; then
    cp config.yaml.example config.yaml
    echo -e "${YELLOW}config.yaml created. Fill in your Robinhood credentials, then re-run this script.${NC}"
    echo ""
    echo "  Edit config.yaml:"
    echo "    robinhood:"
    echo "      username: your_email@example.com"
    echo "      password: your_password"
    echo ""
    exit 1
fi

# ── 3. Install dependencies ───────────────────────────────────────────────────
echo "Installing backend dependencies..."
pip3 install -r backend/requirements.txt -q

echo "Installing frontend dependencies..."
(cd frontend && npm install --silent)

# ── 4. Authenticate (one-time) ────────────────────────────────────────────────
if [ ! -f ~/.tokens/robinhood.pickle ]; then
    echo ""
    echo -e "${YELLOW}First-time setup: Robinhood authentication required.${NC}"
    echo "You'll need to approve the login on your Robinhood app and enter your 2FA code."
    echo ""
    python3 backend/authenticate.py
    echo ""
fi

# ── 5. Start backend (background) ─────────────────────────────────────────────
echo "Starting backend on http://localhost:8000 ..."
# Kill any existing process on port 8000 before starting
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
python3 -m backend.main > /tmp/washsale_backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to respond
echo -n "Waiting for backend"
for i in {1..15}; do
    if curl -s http://localhost:8000/auth/status &>/dev/null; then
        echo " ready."
        break
    fi
    echo -n "."
    sleep 1
done

trap "echo ''; echo 'Stopping...'; kill $BACKEND_PID 2>/dev/null; exit 0" INT TERM

# ── 6. Start frontend (foreground — Vite prints the URL here) ─────────────────
echo ""
echo -e "${GREEN}Backend running. Starting frontend — open the URL shown below.${NC}"
echo ""
cd frontend && npm run dev
