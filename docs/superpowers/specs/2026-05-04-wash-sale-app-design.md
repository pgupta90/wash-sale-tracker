# Wash Sale Prevention App — Design Specification

**Date:** 2026-05-04  
**Stack:** React (Vite) + Python (FastAPI) + SQLite

---

## 1. Overview

A single-user web app that helps prevent wash sale violations by syncing Robinhood trade history locally and allowing the user to look up all trades for a given symbol in the past 30 days before placing a new trade. The app does not auto-flag wash sales — it surfaces trade history so the user can make their own judgment.

---

## 2. Architecture & Tech Stack

### Directory Structure

```
/WashSaleApp
  /backend          # FastAPI (Python)
  /frontend         # React (Vite)
  config.yaml       # Robinhood credentials + session token storage
```

### Backend

- **Framework:** FastAPI (Python)
- **Robinhood integration:** `robin_stocks` library
- **Database:** SQLite (local, stores synced trade history)
- **Endpoints:** `POST /auth`, `POST /sync`, `GET /sync/status`, `GET /trades?symbol=&expiry=&strike=`
- **Auth flow:** Read username/password from `config.yaml` → Robinhood login → MFA prompt on CLI if needed → persist session token back to `config.yaml`

### Frontend

- **Framework:** React + Vite
- Runs on `localhost:5173`, talks to backend at `localhost:8000`
- Three UI zones: sync status bar, search filters, results table

### Data Flow

1. User runs `python backend/main.py` → server starts, auto-attempts login using `config.yaml`
2. User runs `npm run dev` in `/frontend` → React app opens in browser
3. User clicks "Sync Now" → backend fetches all stock + options trades from Robinhood → stores in SQLite
4. User searches symbol (+ optional expiry/strike) → backend queries SQLite for last 30 days → returns results to React

---

## 3. Data Model

Single `trades` table in SQLite:

| Column | Type | Notes |
|---|---|---|
| `id` | TEXT | Robinhood order ID (primary key) |
| `symbol` | TEXT | e.g. `META` |
| `platform` | TEXT | Always `robinhood` |
| `trade_type` | TEXT | `option` or `stock` |
| `option_type` | TEXT | `call`, `put`, or null for stocks |
| `strategy` | TEXT | `single`, `iron_condor`, `call_spread`, `put_spread`; null for stock trades |
| `side` | TEXT | `buy` or `sell` |
| `expiration_date` | DATE | null for stocks |
| `strike_price` | DECIMAL | null for stocks |
| `trade_price` | DECIMAL | Price per share/contract at execution |
| `quantity` | DECIMAL | Number of shares or contracts |
| `status` | TEXT | `open` or `closed` |
| `executed_at` | DATETIME | Trade execution timestamp |
| `synced_at` | DATETIME | When this record was last pulled from Robinhood |

**Search query logic:** filter by `symbol` (required) + optional `expiration_date` + optional `strike_price`, where `executed_at >= now − 30 days`.

---

## 4. UI Layout & Color Coding

### Layout (single page, three zones)

**Zone 1 — Sync Bar (top)**  
Shows "Last synced: [datetime]" and a "Sync Now" button. During sync: button shows spinner and is disabled; timestamp replaced with "Syncing..."

**Zone 2 — Search Filters**  
Symbol field (required), Expiry date field (optional), Strike price field (optional), Search button.

**Zone 3 — Results Table**  
Shows count ("X trades in last 30 days"). Empty state: "No trades found for [SYMBOL] in the last 30 days".

### Results Table Columns (in order)

`Symbol` | `Platform` | `Trade Type` | `Option Type` | `Strategy` | `Side` | `Expiry` | `Strike` | `Trade Price` | `Qty` | `Status` | `Date`

### Color Coding

| Condition | Visual Treatment |
|---|---|
| Side = `buy` | Green text/badge |
| Side = `sell` | Red text/badge |
| Status = `open` | Bold row, white background |
| Status = `closed` | Normal weight, light gray background |
| Option Type = `call` | Blue badge |
| Option Type = `put` | Orange badge |
| Trade Type = stock (N/A) | Gray badge |
| Strategy = `iron_condor` / spread | Purple badge on Strategy column |

---

## 5. Acceptance Criteria

### Authentication
- **AC1:** App reads `config.yaml` and logs in without manual input when credentials + valid session token are present.
- **AC2:** When session token is expired/missing, app prints MFA prompt to CLI, accepts input, and persists new token to `config.yaml`.
- **AC3:** Invalid credentials produce a clear error message; app does not crash.

### Sync
- **AC4:** "Last synced" timestamp is displayed in the UI and updates after each successful sync.
- **AC5:** Manual sync fetches all stock orders and all options orders (including legs of multi-leg strategies like iron condors).
- **AC6:** Re-syncing does not create duplicate records — existing rows are upserted by Robinhood order ID.
- **AC7:** Sync status (in-progress / complete / failed) is visible in the UI.

### Search
- **AC8:** Searching a symbol returns all trades for that symbol within the past 30 days.
- **AC9:** Adding expiry date filter narrows results to that expiry only.
- **AC10:** Adding strike price filter narrows results further to that exact strike.
- **AC11:** Results show all 12 columns: Symbol, Platform, Trade Type, Option Type, Strategy, Side, Expiry, Strike, Trade Price, Qty, Status, Date.
- **AC12:** Color coding distinguishes buy vs. sell and open vs. closed at a glance.
- **AC13:** Empty results show a clear "no trades found" message, not a blank table.

---

## 6. Test Plan — Incremental Build Order

Each phase is independently testable before the next is built.

### Phase 1 — Auth (backend only, no UI)
- Run `python backend/main.py` with valid config → verify no MFA prompt, server starts.
- Clear session token from config → verify MFA prompt appears on CLI, new token written back.
- Use wrong password → verify error message, server still starts (unauthenticated state).
- **Tool:** `curl http://localhost:8000/auth/status`

### Phase 2 — Sync (backend only)
- Hit `POST /sync` via curl → verify SQLite `trades` table is populated.
- Inspect rows for at least one stock order and one options order.
- Re-run sync → verify row count stays the same (no duplicates).
- Verify iron condor legs appear as separate rows with `strategy=iron_condor`.
- **Tool:** `sqlite3 backend/db.sqlite "SELECT trade_type, strategy, COUNT(*) FROM trades GROUP BY trade_type, strategy"`

### Phase 3 — Search API (backend only)
- `GET /trades?symbol=META` → verify only META trades, within last 30 days.
- `GET /trades?symbol=META&expiry=2025-06-20` → verify filtered results.
- `GET /trades?symbol=META&expiry=2025-06-20&strike=500` → verify exact match.
- `GET /trades?symbol=ZZZZ` → verify empty array response, not an error.
- **Tool:** curl or Postman against `localhost:8000`

### Phase 4 — React UI (frontend, with real backend)
- Sync status bar shows last synced time and "Sync Now" button.
- Clicking "Sync Now" triggers sync and updates timestamp.
- Search by symbol returns populated table with all 12 columns.
- Verify color coding: buy vs. sell visually distinct; open vs. closed visually distinct.
- Search with no results shows "no trades found" message.
- **Tool:** Manual browser testing + React DevTools

### Phase 5 — End-to-End
- Full flow from cold start: no token → MFA prompt → sync → search → results.
- Verify a known options trade (e.g., a META put placed recently) appears correctly in results.
