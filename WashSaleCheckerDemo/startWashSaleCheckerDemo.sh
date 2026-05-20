#!/bin/bash

# Usage: bash startWashSaleCheckerDemo.sh  (run from the WashSaleCheckerDemo directory)
# No Robinhood account needed — uses pre-loaded demo trade data.

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "=== Wash Sale Checker — Demo ==="
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

# ── 2. Install dependencies ───────────────────────────────────────────────────
echo "Installing backend dependencies..."
pip3 install fastapi "uvicorn[standard]" PyYAML -q

echo "Installing frontend dependencies..."
(cd frontend && npm install --silent)

# ── 3. Start demo backend on port 8001 (background) ──────────────────────────
echo "Starting demo backend on http://localhost:8001 ..."
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
python3 -m backend.main > /tmp/washsale_demo_backend.log 2>&1 &
BACKEND_PID=$!

echo -n "Waiting for backend"
for i in {1..15}; do
    if curl -s http://localhost:8001/auth/status &>/dev/null; then
        echo " ready."
        break
    fi
    echo -n "."
    sleep 1
done

trap "echo ''; echo 'Stopping demo...'; kill $BACKEND_PID 2>/dev/null; exit 0" INT TERM

# ── 4. Start frontend (foreground — Vite prints the URL) ──────────────────────
echo ""
echo -e "${GREEN}Demo backend running. Starting frontend — open the URL shown below.${NC}"
echo -e "${YELLOW}Try searching: AAPL, NVDA, AMZN (wash sale examples), SPY, META, MSFT, TSLA, QQQ${NC}"
echo ""
cd frontend && npm run dev
