# Wash Sale Checker — Demo

A standalone demo of the Wash Sale Checker that runs entirely on your machine with no Robinhood account needed. It uses pre-loaded sample trade data covering stocks and options strategies.

---

## Prerequisites

| Requirement | Version | Install |
|---|---|---|
| Python | 3.9+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org/) |

Verify:

```bash
python3 --version   # 3.9+
node --version      # 20+
```

---

## Run the demo

From the `WashSaleCheckerDemo` directory:

```bash
bash startWashSaleCheckerDemo.sh
```

The script will:

1. Install backend Python dependencies (`fastapi`, `uvicorn`, `PyYAML`)
2. Install frontend Node dependencies
3. Start the demo backend on `http://localhost:8001`
4. Start the frontend — Vite will print the URL (usually `http://localhost:5173`)

Open the URL in your browser to use the app.

---

## Try these searches

| Symbol | What it shows |
|---|---|
| AAPL | Wash sale example — stock buy after a loss |
| NVDA | Wash sale example — rapid buy/sell/buy |
| META | Wash sale example — overlapping window |
| AMZN | Mixed stock trades |
| MSFT | Stock with gain/loss mix |
| TSLA | High-volume stock trades |
| SPY | Iron condor options strategy |
| QQQ | Iron butterfly options strategy |

---

## Stop the demo

Press `Ctrl+C` in the terminal running the script. The backend process is shut down automatically.

---

## What's in the demo

```
WashSaleCheckerDemo/
  backend/          FastAPI + SQLite, pre-seeded with dummy trades (port 8001)
  frontend/         React + Vite (same UI as the full app)
  config.yaml       Demo config — search_days: 30, dummy credentials
  startWashSaleCheckerDemo.sh
```

The demo backend runs on port **8001** (not 8000) to avoid conflicting with a live instance.

---

## Notes

- No real data, no Robinhood credentials, no network calls to Robinhood.
- All data is pre-seeded in a local SQLite database inside `backend/`.
- To use the full app with your own Robinhood account, see the [main README](../README.md).
