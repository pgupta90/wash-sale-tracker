# Wash Sale Checker

A personal tool to look up recent Robinhood trade history so you can avoid wash sale violations before placing a new trade.

> **What is a wash sale?** The IRS wash sale rule disallows a tax loss when you sell a security at a loss and buy the same or substantially identical security within 30 days before or after the sale. This app helps you check your recent trade history so you can make informed decisions — it does not flag or enforce anything automatically.

---

## Features

- Sync stock and options orders from **Robinhood**
- Search trades by **symbol**, **expiry date**, and **strike price**
- Color-coded results table — buy/sell, open/closed, call/put at a glance
- Configurable search window (default: last 30 days)

---

## Architecture

```
frontend/   React + Vite (port 5173)
backend/    FastAPI + SQLite (port 8000)
```

The backend syncs trade data from Robinhood into a local SQLite database. The frontend queries the backend to display results. All data stays on your machine.

---

## Prerequisites

Before running the app, make sure you have the following installed:

| Requirement | Version | Install |
|---|---|---|
| Python | 3.9+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org/) |
| pip | latest | comes with Python |
| npm | latest | comes with Node.js |

To verify:

```bash
python3 --version    # should be 3.9+
node --version       # should be 20+
pip3 --version
npm --version
```

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd WashSaleApp

# Backend
pip3 install -r backend/requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### 2. Configure credentials

Copy the example config and fill in your Robinhood credentials:

```bash
cp config.yaml.example config.yaml
```

Edit `config.yaml`:

```yaml
robinhood:
  username: your_email@example.com
  password: your_password

settings:
  search_days: 30    # how many days back to search (e.g. 30, 60, 365)
```

> `config.yaml` is gitignored and never committed.

### 3. Authenticate with Robinhood (one-time)

```bash
python3 backend/authenticate.py
```

This opens an interactive prompt. You'll need to:
1. Approve the login notification on your Robinhood app
2. Enter your Google Authenticator code (if enabled)

Session tokens are saved to `~/.tokens/robinhood.pickle` and reloaded automatically on each app restart.

### 4. Start the app

Open two terminal windows:

```bash
# Terminal 1 — backend
python3 -m backend.main

# Terminal 2 — frontend
cd frontend && npm run dev
```

Open **http://localhost:5173** in your browser.

---

## Using the App

### Sync

At the top of the page, click **Sync Now** to pull fresh trade data from Robinhood. The sync fetches the last 60 days of stock and options orders.

### Search

Enter a ticker symbol (required) and optionally filter by:

- **Expiry** — options expiration date in `YYYY-MM-DD` format (paste directly from the results table)
- **Strike** — options strike price

Click **Search** to see all matching trades within your configured `search_days` window.

### Results table

| Column | Description |
|---|---|
| Symbol | Ticker |
| Trade Type | `stock` or `option` |
| Option Type | `call` / `put` badge |
| Strategy | e.g. `single`, `iron_condor` |
| Side | `buy` (green) / `sell` (red) |
| Expiry | Options expiration date |
| Strike | Options strike price |
| Trade Price | Execution price |
| Qty | Number of shares or contracts |
| Status | `open` (bold) or `closed` (dimmed) |
| Date | Execution date |

### Changing the search window

Edit `search_days` in `config.yaml` and restart the backend:

```yaml
settings:
  search_days: 60    # show last 60 days of results
```

---

## Project Structure

```
backend/
  authenticate.py    # One-time Robinhood auth script
  auth.py            # Robinhood session management
  sync.py            # Robinhood order sync
  database.py        # SQLite helpers
  config.py          # Config loader
  models.py          # Pydantic response models
  main.py            # FastAPI app entry point
  routes/
    auth.py          # Auth status endpoint
    sync.py          # Sync trigger endpoint
    trades.py        # Trade search endpoint
  tests/             # pytest test suite

frontend/
  src/
    api.js           # Backend API client
    App.jsx          # Root component
    App.css          # Styles
    components/
      AuthBar.jsx        # Robinhood connection status
      RobinhoodModal.jsx # Robinhood login modal
      SyncBar.jsx        # Sync controls and status
      SearchFilters.jsx  # Symbol/expiry/strike form
      TradesTable.jsx    # Color-coded results table

config.yaml.example  # Template — copy to config.yaml and fill in credentials
```

---

## Running Tests

```bash
cd WashSaleApp
python3 -m pytest backend/tests/
```

---

## Notes

- This app uses the **unofficial Robinhood API** via `robin_stocks`. Use at your own discretion and review Robinhood's Terms of Service.
- No data leaves your machine. All trade history is stored locally in `backend/db.sqlite`.
- This tool is for **informational purposes only** and does not provide tax or legal advice.
