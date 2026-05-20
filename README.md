# Wash Sale Checker

A personal tool to look up recent Robinhood trade history so you can avoid wash sale violations before placing a new trade.

> **What is a wash sale?** The IRS wash sale rule disallows a tax loss when you sell a security at a loss and buy the same or substantially identical security within 30 days before or after the sale. This app helps you check your recent trade history so you can make informed decisions — it does not flag or enforce anything automatically.

---

## Features

- Sync stock and options orders from **Robinhood**
- Search trades by **symbol**, **expiry date** (date picker), and **strike price**
- Color-coded results table — buy/sell, open/closed, call/put at a glance
- Supported strategies: `single`, `call_spread`, `put_spread`, `iron_condor`, `iron_butterfly`
- Configurable search window (default: last 365 days)
- **Demo mode** — run without a Robinhood account using pre-loaded sample data

---

## Architecture

```
frontend/   React + Vite (port 5173)
backend/    FastAPI + SQLite (port 8000)
```

The backend syncs trade data from Robinhood into a local SQLite database. The frontend queries the backend to display results. All data stays on your machine.

---

## Prerequisites

| Requirement | Version | Install |
|---|---|---|
| Python | 3.9+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org/) |
| pip | latest | comes with Python |
| npm | latest | comes with Node.js |

Verify your versions:

```bash
python3 --version    # should be 3.9+
node --version       # should be 20+
pip3 --version
npm --version
```

---

## Demo (no Robinhood account needed)

To explore the app with pre-loaded sample data:

```bash
cd WashSaleCheckerDemo
bash startWashSaleCheckerDemo.sh
```

Open the URL printed by Vite (usually `http://localhost:5173`). Try searching: **AAPL**, **NVDA**, **META** (wash sale examples), **SPY** (iron condor), **QQQ** (iron butterfly), **AMZN**, **MSFT**, **TSLA**.

---

## Quickstart

### 1. Clone the repo

```bash
git clone <repo-url>
cd WashSaleApp
```

### 2. Add your credentials

```bash
cp config.yaml.example config.yaml
```

Edit `config.yaml` with your Robinhood login:

```yaml
robinhood:
  username: your_email@example.com
  password: your_password

settings:
  search_days: 365    # how many days back to search
```

> `config.yaml` is gitignored and never committed.

### 3. Run the start script

```bash
bash startWashSaleChecker.sh
```

The script will, in order:

1. **Install** backend and frontend dependencies
2. **Authenticate** with Robinhood (one-time — you'll approve the login on your phone and enter your 2FA code). Session is saved to `~/.tokens/robinhood.pickle` and reused on every future run.
3. **Start the backend** on `http://localhost:8000`
4. **Start the frontend** — Vite will print the URL (usually `http://localhost:5173`)

> On subsequent runs, step 2 is skipped automatically since the session is already saved.

---

## Manual startup (alternative)

If you prefer to run each step yourself:

```bash
# One-time: authenticate with Robinhood
python3 backend/authenticate.py

# Terminal 1 — backend
python3 -m backend.main

# Terminal 2 — frontend
cd frontend && npm run dev
```

---

## Using the App

### Sync

Click **Sync Now** at the top of the page to pull fresh trade data. The sync fetches the last 60 days of stock and options orders from Robinhood.

### Search

Enter a ticker symbol (required) and optionally filter by:

- **Expiry** — use the date picker; the label updates to show the selected date (e.g. "Expiry — Aug 21, 2026"). Click × to clear.
- **Strike** — options strike price

Results show all matching trades within your configured `search_days` window.

### Results table

A date range header shows the span of trades returned (e.g. "Trades between Feb 3, 2026 – Apr 28, 2026").

| Column | Description |
|---|---|
| Symbol | Ticker |
| Trade Type | `stock` or `option` |
| Option / Strategy | Option type (`call`/`put`) and strategy badge (`single`, `call_spread`, `iron_condor`, `iron_butterfly`, …) |
| Action | `Buy`, `Sell`, `Buy to Open`, `Sell to Close`, etc. |
| Strike | Options strike price |
| Trade Price | Execution price (premium for options, share price for stocks) |
| Qty | Shares or contracts |
| Status | `open` or `closed` |
| Realized G/L | Computed gain/loss on closed positions |
| Trade Open Date | Execution date |
| Expiry | Options expiration date |

### Changing the search window

Edit `search_days` in `config.yaml` and restart the backend:

```yaml
settings:
  search_days: 60
```

---

## Project Structure

```
startWashSaleChecker.sh     # One-command startup (requires Robinhood credentials)

WashSaleCheckerDemo/        # Standalone demo — no credentials needed
  backend/                  # FastAPI + SQLite with pre-seeded dummy data (port 8001)
  frontend/                 # React + Vite (shares same UI components)
  config.yaml               # Demo config (search_days: 365, dummy credentials)
  startWashSaleCheckerDemo.sh

backend/
  authenticate.py      # One-time Robinhood auth script
  auth.py              # Robinhood session management
  sync.py              # Robinhood order sync
  database.py          # SQLite helpers
  config.py            # Config loader
  models.py            # Pydantic response models
  main.py              # FastAPI app entry point
  routes/
    auth.py            # Auth status endpoint
    sync.py            # Sync trigger endpoint
    trades.py          # Trade search endpoint
  tests/               # pytest test suite

frontend/
  src/
    api.js             # Backend API client
    App.jsx            # Root component
    App.css            # Styles
    components/
      AuthBar.jsx        # Robinhood connection status
      RobinhoodModal.jsx # Robinhood login modal
      SyncBar.jsx        # Sync controls and status
      SearchFilters.jsx  # Symbol/expiry/strike form
      TradesTable.jsx    # Color-coded results table

config.yaml.example    # Template — copy to config.yaml and fill in credentials
```

---

## Running Tests

```bash
python3 -m pytest backend/tests/
```

---

## Notes

- This app uses the **unofficial Robinhood API** via `robin_stocks`. Use at your own discretion and review Robinhood's Terms of Service.
- No data leaves your machine. All trade history is stored locally in `backend/db.sqlite`.
- This tool is for **informational purposes only** and does not provide tax or legal advice.
