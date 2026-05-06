# Charles Schwab Integration Design

## Goal

Add Charles Schwab as a second brokerage platform to the WashSaleApp. Users can authenticate with Schwab, sync their last 60 days of stock and options orders, and search trades across both Robinhood and Schwab in the same UI.

## Architecture

The Schwab stack mirrors the existing Robinhood stack. No existing Robinhood code is modified — a parallel set of files handles Schwab auth and sync.

### New files

| File | Responsibility |
|---|---|
| `backend/schwab_authenticate.py` | One-time interactive OAuth2 script; saves tokens to `~/.tokens/schwab_token.json` |
| `backend/schwab_auth.py` | Loads saved schwab-py client; `get_schwab_client()` and `get_schwab_status()` |
| `backend/schwab_sync.py` | Fetches stock + option orders from Schwab API; maps to Trade schema; upserts to DB |

### Modified files

| File | Change |
|---|---|
| `config.yaml` | Add `schwab:` section with `client_id`, `client_secret`, `redirect_uri` |
| `backend/routes/sync.py` | Add `POST /sync/schwab` and `GET /sync/schwab/status` endpoints |
| `backend/routes/auth.py` | Add `GET /auth/schwab/status` endpoint |
| `backend/main.py` | Log Schwab auth status on startup |
| `frontend/src/components/SyncBar.jsx` | Add Schwab row with its own sync button and last-synced time |

## Python Version

`schwab-py` requires Python 3.10+. Upgrade via Homebrew:

```bash
brew install python@3.11
pip3.11 install schwab-py
```

All Schwab scripts use `python3.11`. Existing Robinhood scripts stay on system Python 3.9.

## Authentication Flow

### One-time setup

```bash
python3.11 backend/schwab_authenticate.py
```

1. Script reads `client_id`, `client_secret`, `redirect_uri` from `config.yaml`
2. schwab-py generates and prints an authorization URL
3. User opens URL in browser, logs into Schwab, approves the app
4. Schwab redirects to `redirect_uri` — user copies the full redirected URL and pastes it into the terminal
5. schwab-py exchanges the code for tokens and saves to `~/.tokens/schwab_token.json`

**Redirect URI:** `https://127.0.0.1` — must be registered exactly in the Schwab developer portal. schwab-py starts a local HTTPS listener to capture the callback automatically.

### Token lifecycle

- Access tokens expire every 30 minutes — schwab-py auto-refreshes transparently
- Refresh tokens expire every 7 days — user re-runs `schwab_authenticate.py`
- Backend startup: loads client from token file; logs warning if missing/expired

### Developer portal setup (one-time manual step)

1. Create account at developer.schwab.com
2. Register a new app — note the `App Key` (client_id) and `Secret` (client_secret)
3. Set redirect URI to `https://127.0.0.1`
4. Add credentials to `config.yaml` under `schwab:`

## Sync Flow

### Endpoint: `POST /sync/schwab`

1. Load schwab-py client from `~/.tokens/schwab_token.json`
2. Call `client.get_account_numbers()` → extract `account_hash`
3. Call `client.get_orders_for_account(account_hash, from_entered_datetime=cutoff, to_entered_datetime=now, status=Status.FILLED)` with 60-day cutoff
4. Map each order to the Trade schema (see field mapping below)
5. Upsert to SQLite via existing `upsert_trade()`
6. Return sync status

### Field mapping (Schwab → Trade)

| Schwab field | Trade field | Notes |
|---|---|---|
| `orderId` | `id` | Prefixed with `schwab-` to avoid collisions with Robinhood IDs |
| `orderLegCollection[0].instrument.symbol` | `symbol` | |
| `'schwab'` | `platform` | Hardcoded |
| `orderLegCollection[0].instrument.assetType` | `trade_type` | `EQUITY` → `stock`, `OPTION` → `option` |
| `orderLegCollection[0].instrument.putCall` | `option_type` | `PUT`/`CALL`/`None` |
| `None` | `strategy` | Not provided by Schwab API |
| `orderLegCollection[0].instruction` | `side` | `BUY` → `buy`, `SELL` → `sell` |
| `orderLegCollection[0].instrument.expirationDate` | `expiration_date` | Options only |
| `orderLegCollection[0].instrument.strikePrice` | `strike_price` | Options only |
| `orderActivityCollection[0].executionLegs[0].price` | `trade_price` | |
| `filledQuantity` | `quantity` | |
| `FILLED` → `closed`, else `open` | `status` | |
| `closeTime` | `executed_at` | |

### Endpoint: `GET /sync/schwab/status`

Returns `{status, last_synced, error}` — same shape as existing `GET /sync/status`.

## Frontend Changes

`SyncBar.jsx` gains a second row for Schwab. Each row is independent:

```
[ Robinhood ]  Last synced: 2 min ago  [ Sync Now ]
[ Schwab    ]  Not yet synced          [ Sync Now ]
```

Each "Sync Now" button calls its own endpoint (`POST /sync` vs `POST /sync/schwab`). Auth status for each platform shown as a badge (authenticated / not authenticated).

## Auth Status Endpoint

`GET /auth/schwab/status` → `{authenticated: bool, error: string|null}`

Checks by attempting to load the schwab-py client from the saved token file. If the token is missing, expired, or invalid, returns `authenticated: false`.

## Error Handling

- Missing token file → startup warning, `GET /auth/schwab/status` returns `authenticated: false`
- Expired refresh token → sync returns error, user re-runs `schwab_authenticate.py`
- API errors during sync → `_schwab_sync_state['error']` set, returned in status endpoint

## Testing

- `test_schwab_auth.py` — mock schwab-py client; test `get_schwab_status()` returns correct shape
- `test_schwab_sync.py` — mock API responses; test field mapping for stock and option orders
- `test_routes_schwab_sync.py` — test sync endpoints return correct status codes and response shape
