# Wash Sale Checker

A personal tool to look up recent trade history across Robinhood and Charles Schwab — so you can avoid wash sale violations before placing a new trade.

> **What is a wash sale?** The IRS wash sale rule disallows a tax loss when you sell a security at a loss and buy the same or substantially identical security within 30 days before or after the sale. This app helps you check your recent trade history so you can make informed decisions — it does not flag or enforce anything automatically.

---

## Features

- Sync stock and options orders from **Robinhood** and **Charles Schwab**
- Search trades by **symbol**, **expiry date**, and **strike price**
- Color-coded results table — buy/sell, open/closed, call/put at a glance
- Configurable search window (default: last 30 days)
- Trades from both platforms shown together

---

## Architecture

```
frontend/   React + Vite (port 5173)
backend/    FastAPI + SQLite (port 8000)
```

The backend syncs trade data from brokerage APIs into a local SQLite database. The frontend queries the backend to display results. All data stays on your machine.

---

## Setup

### Prerequisites

- Python 3.9+
- Python 3.11+ (required for Charles Schwab integration)
- Node.js 20+

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

Copy the example config and fill in your credentials:

```bash
cp config.yaml.example config.yaml
```

Edit `config.yaml`:

```yaml
robinhood:
  username: your_email@example.com
  password: your_password

schwab:
  client_id: your_schwab_app_key
  client_secret: your_schwab_secret
  redirect_uri: https://127.0.0.1

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

Session tokens are saved to `~/.tokens/robinhood.pickle` and reloaded automatically on each restart.

### 4. Authenticate with Charles Schwab (one-time)

First, register an app at [developer.schwab.com](https://developer.schwab.com):
1. Create a developer account (separate from your trading account)
2. Register a new app — set redirect URI to `https://127.0.0.1`
3. Copy the **App Key** and **Secret** into `config.yaml`

Then run:

```bash
python3.11 backend/schwab_authenticate.py
```

A browser will open for OAuth2 approval. Tokens are saved to `~/.tokens/schwab_token.json`.

> Schwab tokens expire after 7 days. Re-run this script to refresh.

### 5. Start the app

```bash
# Terminal 1 — backend
python3 -m backend.main

# Terminal 2 — frontend
cd frontend && npm run dev
```

Open **http://localhost:5173**

---

## Using the App

### Sync bar

At the top of the page, two sync rows show the last sync time for each platform. Click **Sync Now** to pull fresh data.

- Robinhood sync fetches the last 60 days of stock and options orders
- Schwab sync fetches the last 60 days of filled orders

### Search

Enter a ticker symbol (required) and optionally filter by:

- **Expiry** — paste an expiry date directly from the results table in `YYYY-MM-DD` format
- **Strike** — options strike price

Click **Search** to see all matching trades within your configured `search_days` window.

### Results table

| Column | Description |
|---|---|
| Symbol | Ticker |
| Platform | `robinhood` or `schwab` |
| Trade Type | `stock` or `option` |
| Option Type | `call` / `put` badge |
| Strategy | e.g. `single`, `iron_condor` |
| Side | `buy` (green) / `sell` (red) |
| Expiry | Options expiration date — copy directly into the Expiry search filter |
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
  authenticate.py          # Robinhood one-time auth script
  schwab_authenticate.py   # Schwab one-time auth script
  auth.py                  # Robinhood session management
  schwab_auth.py           # Schwab session management
  sync.py                  # Robinhood order sync
  schwab_sync.py           # Schwab order sync
  database.py              # SQLite helpers
  config.py                # Config loader
  models.py                # Pydantic response models
  main.py                  # FastAPI app entry point
  routes/
    auth.py                # Auth status endpoints
    sync.py                # Sync trigger endpoints
    trades.py              # Trade search endpoint
  tests/                   # pytest test suite

frontend/
  src/
    api.js                 # Backend API client
    App.jsx                # Root component
    App.css                # Styles
    components/
      SyncBar.jsx          # Platform sync controls
      SearchFilters.jsx    # Symbol/expiry/strike form
      TradesTable.jsx      # Color-coded results table

config.yaml.example        # Template — copy to config.yaml and fill in credentials
```

---

## Notes

- This app uses **unofficial APIs** for Robinhood (via `robin_stocks`). Use at your own discretion and review Robinhood's Terms of Service.
- Charles Schwab integration uses the **official Schwab Developer API**.
- No data leaves your machine. All trade history is stored locally in `backend/db.sqlite`.
- This tool is for **informational purposes only** and does not provide tax or legal advice.
