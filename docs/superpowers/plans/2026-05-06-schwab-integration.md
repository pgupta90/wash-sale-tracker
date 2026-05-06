# Charles Schwab Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Charles Schwab as a second brokerage platform — auth, sync, and UI — alongside the existing Robinhood integration.

**Architecture:** Three new backend modules (`schwab_auth.py`, `schwab_authenticate.py`, `schwab_sync.py`) mirror the Robinhood pattern. New routes (`POST /sync/schwab`, `GET /sync/schwab/status`, `GET /auth/schwab/status`) are added to existing route files. The frontend SyncBar gains a second row for Schwab. The `platform` column already exists in the DB — no schema changes needed.

**Tech Stack:** Python 3.11 (required by schwab-py), schwab-py v1.5+, FastAPI, SQLite, React/Vite.

---

## File Map

| File | Action | What changes |
|---|---|---|
| `backend/schwab_auth.py` | Create | `get_schwab_client()`, `get_schwab_status()` |
| `backend/schwab_authenticate.py` | Create | One-time OAuth2 interactive script |
| `backend/schwab_sync.py` | Create | `sync_schwab_orders()` — fetches + maps + upserts |
| `backend/database.py` | Modify | Add `get_schwab_last_synced()`, `set_schwab_last_synced()` |
| `backend/routes/auth.py` | Modify | Add `GET /auth/schwab/status` |
| `backend/routes/sync.py` | Modify | Add `POST /sync/schwab`, `GET /sync/schwab/status` |
| `backend/main.py` | Modify | Log Schwab auth status on startup |
| `backend/tests/test_schwab_auth.py` | Create | Tests for `get_schwab_status()` |
| `backend/tests/test_schwab_sync.py` | Create | Tests for field mapping + upsert |
| `backend/tests/test_routes_schwab.py` | Create | Route integration tests |
| `frontend/src/api.js` | Modify | Add `getSchwabSyncStatus()`, `triggerSchwabSync()` |
| `frontend/src/components/SyncBar.jsx` | Modify | Add Schwab row |
| `frontend/src/App.css` | Modify | Add `.sync-bar-row`, `.sync-platform` styles |
| `config.yaml` | Modify | Add `schwab:` section |

---

## Task 1: Install Python 3.11 and schwab-py

**Files:** none (environment setup)

- [ ] **Step 1: Install Python 3.11 via Homebrew**

```bash
brew install python@3.11
```

Expected: Python 3.11.x installed at `/opt/homebrew/bin/python3.11`

- [ ] **Step 2: Verify Python 3.11**

```bash
python3.11 --version
```

Expected: `Python 3.11.x`

- [ ] **Step 3: Install schwab-py**

```bash
pip3.11 install schwab-py
```

Expected: `Successfully installed schwab-py-...`

- [ ] **Step 4: Verify schwab-py import**

```bash
python3.11 -c "import schwab; print('schwab-py OK', schwab.__version__)"
```

Expected: `schwab-py OK 1.5.x` (or similar)

---

## Task 2: Add Schwab credentials to config.yaml

**Files:**
- Modify: `config.yaml`

- [ ] **Step 1: Add the schwab section**

Open `config.yaml` and add the following section (keep the existing `robinhood:` section intact):

```yaml
schwab:
  client_id: your_schwab_app_key_here
  client_secret: your_schwab_secret_here
  redirect_uri: https://127.0.0.1
```

> The user fills in `client_id` and `client_secret` from developer.schwab.com after registering an app with redirect URI set to `https://127.0.0.1`.

- [ ] **Step 2: Verify config loads**

```bash
python3 -c "from backend.config import load_config; c = load_config(); print(list(c.get('schwab', {}).keys()))"
```

Expected: `['client_id', 'client_secret', 'redirect_uri']`

---

## Task 3: schwab_auth.py + tests

**Files:**
- Create: `backend/schwab_auth.py`
- Create: `backend/tests/test_schwab_auth.py`

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_schwab_auth.py`:

```python
from unittest.mock import patch, MagicMock
from backend.schwab_auth import get_schwab_status

def test_get_schwab_status_authenticated():
    with patch('backend.schwab_auth.schwab.auth.client_from_token_file') as mock_load:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_client.get_account_numbers.return_value = mock_response
        mock_load.return_value = mock_client
        status = get_schwab_status()
    assert status['authenticated'] is True

def test_get_schwab_status_missing_token():
    with patch('backend.schwab_auth.schwab.auth.client_from_token_file') as mock_load:
        mock_load.side_effect = FileNotFoundError('token not found')
        status = get_schwab_status()
    assert status['authenticated'] is False
    assert 'error' in status

def test_get_schwab_status_expired_token():
    with patch('backend.schwab_auth.schwab.auth.client_from_token_file') as mock_load:
        mock_load.side_effect = Exception('401 Unauthorized')
        status = get_schwab_status()
    assert status['authenticated'] is False
    assert 'error' in status
```

- [ ] **Step 2: Run to verify they fail**

```bash
python3 -m pytest backend/tests/test_schwab_auth.py -v
```

Expected: 3 failures with `ModuleNotFoundError` or `ImportError`

- [ ] **Step 3: Implement schwab_auth.py**

Create `backend/schwab_auth.py`:

```python
import os
import schwab
from backend.config import load_config

TOKEN_PATH = os.path.expanduser('~/.tokens/schwab_token.json')


def get_schwab_client():
    config = load_config()
    creds = config.get('schwab', {})
    return schwab.auth.client_from_token_file(
        token_path=TOKEN_PATH,
        api_key=creds.get('client_id', ''),
        app_secret=creds.get('client_secret', ''),
    )


def get_schwab_status() -> dict:
    try:
        client = get_schwab_client()
        resp = client.get_account_numbers()
        resp.raise_for_status()
        return {'authenticated': True}
    except Exception as e:
        return {'authenticated': False, 'error': str(e)}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest backend/tests/test_schwab_auth.py -v
```

Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add backend/schwab_auth.py backend/tests/test_schwab_auth.py
git commit -m "feat: add schwab_auth module with get_schwab_client and get_schwab_status"
```

---

## Task 4: schwab_authenticate.py (one-time interactive auth script)

**Files:**
- Create: `backend/schwab_authenticate.py`

No TDD — this is an interactive OAuth2 script that requires a browser. Verified manually by running it.

- [ ] **Step 1: Create the script**

Create `backend/schwab_authenticate.py`:

```python
#!/usr/bin/env python3.11
"""
Run this script ONCE to authenticate with Charles Schwab via OAuth2.
Requires Python 3.11+: python3.11 backend/schwab_authenticate.py

Prerequisites:
  1. Create a developer account at developer.schwab.com
  2. Register an app with redirect URI: https://127.0.0.1
  3. Copy the App Key and Secret into config.yaml under schwab:

After running this script, tokens are saved to ~/.tokens/schwab_token.json
The backend will load them automatically on every restart.
Tokens expire after 7 days — re-run this script to refresh.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import schwab
from backend.config import load_config

TOKEN_PATH = os.path.expanduser('~/.tokens/schwab_token.json')


def main():
    config = load_config()
    creds = config.get('schwab', {})
    client_id = creds.get('client_id', '')
    client_secret = creds.get('client_secret', '')
    redirect_uri = creds.get('redirect_uri', 'https://127.0.0.1')

    if not client_id or client_id == 'your_schwab_app_key_here':
        print("ERROR: Add your Schwab App Key and Secret to config.yaml first.")
        print("  1. Go to developer.schwab.com and register an app")
        print("  2. Set redirect URI to: https://127.0.0.1")
        print("  3. Add client_id and client_secret under schwab: in config.yaml")
        sys.exit(1)

    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)

    print("Opening browser for Schwab authentication...")
    print("Log in to Schwab and approve the app. The browser will redirect automatically.")
    print()

    try:
        client = schwab.auth.client_from_login_flow(
            api_key=client_id,
            app_secret=client_secret,
            callback_url=redirect_uri,
            token_path=TOKEN_PATH,
        )
        resp = client.get_account_numbers()
        resp.raise_for_status()
        print()
        print(f"Authentication successful! Tokens saved to {TOKEN_PATH}")
        print("The backend will now load Schwab automatically on every restart.")
        print()
        print("Tokens expire after 7 days. Re-run this script to refresh.")
        print()
        print("Start the backend:  python3 -m backend.main")
    except Exception as e:
        print(f"\nAuthentication failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Verify the script is syntactically valid**

```bash
python3.11 -c "import ast; ast.parse(open('backend/schwab_authenticate.py').read()); print('syntax OK')"
```

Expected: `syntax OK`

- [ ] **Step 3: Commit**

```bash
git add backend/schwab_authenticate.py
git commit -m "feat: add schwab_authenticate.py one-time OAuth2 setup script"
```

---

## Task 5: schwab_sync.py + tests

**Files:**
- Create: `backend/schwab_sync.py`
- Create: `backend/tests/test_schwab_sync.py`

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_schwab_sync.py`:

```python
from unittest.mock import MagicMock
from backend.schwab_sync import sync_schwab_orders
from backend.database import init_db, get_connection

MOCK_ACCOUNT_NUMBERS = [{'accountNumber': '12345678', 'hashValue': 'hash-abc-123'}]

MOCK_STOCK_ORDER = {
    'orderId': 11111,
    'status': 'FILLED',
    'filledQuantity': 10.0,
    'closeTime': '2026-04-20T10:00:00+0000',
    'orderLegCollection': [{
        'instruction': 'BUY',
        'quantity': 10.0,
        'instrument': {
            'symbol': 'AAPL',
            'assetType': 'EQUITY',
        },
    }],
    'orderActivityCollection': [{
        'executionType': 'FILL',
        'executionLegs': [{'price': 175.50, 'quantity': 10.0}],
    }],
}

MOCK_OPTION_ORDER = {
    'orderId': 22222,
    'status': 'FILLED',
    'filledQuantity': 1.0,
    'closeTime': '2026-04-21T14:00:00+0000',
    'orderLegCollection': [{
        'instruction': 'BUY_TO_OPEN',
        'quantity': 1.0,
        'instrument': {
            'symbol': 'AAPL 260620C00175000',
            'assetType': 'OPTION',
            'putCall': 'CALL',
            'strikePrice': 175.0,
            'expirationDate': '2026-06-20',
        },
    }],
    'orderActivityCollection': [{
        'executionType': 'FILL',
        'executionLegs': [{'price': 5.50, 'quantity': 1.0}],
    }],
}


def _make_client(orders):
    client = MagicMock()
    acct_resp = MagicMock()
    acct_resp.json.return_value = MOCK_ACCOUNT_NUMBERS
    client.get_account_numbers.return_value = acct_resp
    orders_resp = MagicMock()
    orders_resp.json.return_value = orders
    client.get_orders_for_account.return_value = orders_resp
    return client


def test_sync_schwab_stock_order_stored(tmp_path):
    db_path = str(tmp_path / 'test.sqlite')
    init_db(db_path)
    client = _make_client([MOCK_STOCK_ORDER])
    count = sync_schwab_orders(client=client, db_path=db_path)
    assert count == 1
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM trades WHERE id='schwab-11111-0'").fetchone()
    assert row['symbol'] == 'AAPL'
    assert row['platform'] == 'schwab'
    assert row['trade_type'] == 'stock'
    assert row['side'] == 'buy'
    assert row['trade_price'] == 175.50
    assert row['quantity'] == 10.0
    assert row['status'] == 'closed'
    assert row['option_type'] is None


def test_sync_schwab_option_order_stored(tmp_path):
    db_path = str(tmp_path / 'test.sqlite')
    init_db(db_path)
    client = _make_client([MOCK_OPTION_ORDER])
    count = sync_schwab_orders(client=client, db_path=db_path)
    assert count == 1
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM trades WHERE id='schwab-22222-0'").fetchone()
    assert row['symbol'] == 'AAPL'
    assert row['trade_type'] == 'option'
    assert row['option_type'] == 'call'
    assert row['strike_price'] == 175.0
    assert row['expiration_date'] == '2026-06-20'
    assert row['side'] == 'buy'


def test_sync_schwab_sell_instruction(tmp_path):
    db_path = str(tmp_path / 'test.sqlite')
    init_db(db_path)
    sell_order = dict(MOCK_STOCK_ORDER)
    sell_order['orderId'] = 33333
    sell_order['orderLegCollection'] = [{
        **MOCK_STOCK_ORDER['orderLegCollection'][0],
        'instruction': 'SELL',
    }]
    client = _make_client([sell_order])
    sync_schwab_orders(client=client, db_path=db_path)
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT side FROM trades WHERE id='schwab-33333-0'").fetchone()
    assert row['side'] == 'sell'


def test_sync_schwab_no_duplicates(tmp_path):
    db_path = str(tmp_path / 'test.sqlite')
    init_db(db_path)
    client = _make_client([MOCK_STOCK_ORDER])
    sync_schwab_orders(client=client, db_path=db_path)
    client2 = _make_client([MOCK_STOCK_ORDER])
    sync_schwab_orders(client=client2, db_path=db_path)
    with get_connection(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
    assert count == 1


def test_sync_schwab_skips_old_orders(tmp_path):
    db_path = str(tmp_path / 'test.sqlite')
    init_db(db_path)
    old_order = dict(MOCK_STOCK_ORDER)
    old_order['orderId'] = 99999
    old_order['closeTime'] = '2020-01-01T10:00:00+0000'
    client = _make_client([old_order])
    count = sync_schwab_orders(client=client, db_path=db_path)
    assert count == 0
```

- [ ] **Step 2: Run to verify they fail**

```bash
python3 -m pytest backend/tests/test_schwab_sync.py -v
```

Expected: 5 failures with `ImportError`

- [ ] **Step 3: Implement schwab_sync.py**

Create `backend/schwab_sync.py`:

```python
from datetime import datetime, timedelta, timezone
from backend.database import upsert_trade
from backend.schwab_auth import get_schwab_client

SYNC_DAYS = 60

INSTRUCTION_MAP = {
    'BUY': 'buy',
    'BUY_TO_OPEN': 'buy',
    'BUY_TO_CLOSE': 'buy',
    'SELL': 'sell',
    'SELL_TO_OPEN': 'sell',
    'SELL_TO_CLOSE': 'sell',
}


def _cutoff_dt() -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=SYNC_DAYS)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_close_time(value: str) -> datetime:
    # Schwab returns '+0000' without colon; Python 3.11 handles this natively
    return datetime.fromisoformat(value.replace('+0000', '+00:00'))


def sync_schwab_orders(client=None, db_path: str = None) -> int:
    """Fetch filled orders from Schwab for the last 60 days and upsert into SQLite."""
    if client is None:
        client = get_schwab_client()

    kwargs = {'db_path': db_path} if db_path else {}
    cutoff = _cutoff_dt()
    now = datetime.now(timezone.utc)

    # Get account hash (required for all order API calls)
    acct_resp = client.get_account_numbers()
    accounts = acct_resp.json()
    account_hash = accounts[0]['hashValue']

    # Fetch filled orders within the 60-day window
    from schwab.client import Client
    orders_resp = client.get_orders_for_account(
        account_hash=account_hash,
        from_entered_datetime=cutoff,
        to_entered_datetime=now,
        status=Client.Order.Status.FILLED,
    )
    orders = orders_resp.json()

    count = 0
    for order in orders:
        close_time = order.get('closeTime')
        if not close_time:
            continue
        executed_dt = _parse_close_time(close_time)
        if executed_dt < cutoff:
            continue

        # Get execution price from the first fill activity
        trade_price = 0.0
        activities = order.get('orderActivityCollection', [])
        if activities:
            exec_legs = activities[0].get('executionLegs', [])
            if exec_legs:
                trade_price = float(exec_legs[0].get('price', 0))

        for leg_idx, leg in enumerate(order.get('orderLegCollection', [])):
            instrument = leg.get('instrument', {})
            asset_type = instrument.get('assetType', '')
            instruction = leg.get('instruction', '')
            raw_symbol = instrument.get('symbol', '')
            # Options symbols include expiry/strike; extract the ticker only
            symbol = raw_symbol.split(' ')[0].upper()
            put_call = instrument.get('putCall', '')

            trade = {
                'id': f"schwab-{order['orderId']}-{leg_idx}",
                'symbol': symbol,
                'platform': 'schwab',
                'trade_type': 'option' if asset_type == 'OPTION' else 'stock',
                'option_type': put_call.lower() if put_call else None,
                'strategy': None,
                'side': INSTRUCTION_MAP.get(instruction, 'buy'),
                'expiration_date': instrument.get('expirationDate'),
                'strike_price': float(instrument['strikePrice']) if instrument.get('strikePrice') else None,
                'trade_price': trade_price,
                'quantity': float(order.get('filledQuantity', 0)),
                'status': 'closed' if order.get('status') == 'FILLED' else 'open',
                'executed_at': close_time,
                'synced_at': _now_iso(),
            }
            upsert_trade(trade, **kwargs)
            count += 1

    return count
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest backend/tests/test_schwab_sync.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add backend/schwab_sync.py backend/tests/test_schwab_sync.py
git commit -m "feat: add schwab_sync module with sync_schwab_orders"
```

---

## Task 6: database.py — add Schwab last-synced helpers

**Files:**
- Modify: `backend/database.py`

- [ ] **Step 1: Add the two functions**

Open `backend/database.py`. After the `set_last_synced` function (around line 76), add:

```python
def get_schwab_last_synced(db_path: str = DB_PATH) -> Optional[str]:
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT value FROM sync_meta WHERE key = 'schwab_last_synced'"
        ).fetchone()
        return row['value'] if row else None

def set_schwab_last_synced(timestamp: str, db_path: str = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO sync_meta (key, value) VALUES ('schwab_last_synced', ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (timestamp,))
```

- [ ] **Step 2: Verify all existing tests still pass**

```bash
python3 -m pytest backend/tests/test_database.py -v
```

Expected: all pass

- [ ] **Step 3: Commit**

```bash
git add backend/database.py
git commit -m "feat: add get_schwab_last_synced and set_schwab_last_synced to database"
```

---

## Task 7: Backend routes + tests

**Files:**
- Modify: `backend/routes/auth.py`
- Modify: `backend/routes/sync.py`
- Create: `backend/tests/test_routes_schwab.py`

- [ ] **Step 1: Write failing route tests**

Create `backend/tests/test_routes_schwab.py`:

```python
from unittest.mock import patch
from fastapi.testclient import TestClient


def get_client():
    with patch('backend.main.login_from_config'), \
         patch('backend.main.get_schwab_status', return_value={'authenticated': False}):
        from backend.main import app
        return TestClient(app)


def test_schwab_auth_status_unauthenticated():
    client = get_client()
    with patch('backend.routes.auth.get_schwab_status', return_value={'authenticated': False, 'error': 'no token'}):
        response = client.get('/auth/schwab/status')
    assert response.status_code == 200
    data = response.json()
    assert data['authenticated'] is False


def test_schwab_auth_status_authenticated():
    client = get_client()
    with patch('backend.routes.auth.get_schwab_status', return_value={'authenticated': True}):
        response = client.get('/auth/schwab/status')
    assert response.status_code == 200
    assert response.json()['authenticated'] is True


def test_schwab_sync_status_never_synced():
    client = get_client()
    with patch('backend.routes.sync.get_schwab_last_synced', return_value=None):
        response = client.get('/sync/schwab/status')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'idle'
    assert data['last_synced'] is None


def test_post_schwab_sync_calls_sync_function():
    client = get_client()
    with patch('backend.routes.sync.sync_schwab_orders', return_value=5) as mock_sync, \
         patch('backend.routes.sync.set_schwab_last_synced') as mock_set, \
         patch('backend.routes.sync.get_schwab_last_synced', return_value='2026-05-06T12:00:00+00:00'):
        response = client.post('/sync/schwab')
    assert response.status_code == 200
    assert response.json()['status'] == 'idle'
    mock_sync.assert_called_once()
    mock_set.assert_called_once()
```

- [ ] **Step 2: Run to verify they fail**

```bash
python3 -m pytest backend/tests/test_routes_schwab.py -v
```

Expected: failures (routes not yet added)

- [ ] **Step 3: Add Schwab auth route to routes/auth.py**

Replace the full content of `backend/routes/auth.py` with:

```python
from fastapi import APIRouter
from backend.auth import get_auth_status
from backend.schwab_auth import get_schwab_status
from backend.models import AuthStatus

router = APIRouter(prefix='/auth', tags=['auth'])

@router.get('/status', response_model=AuthStatus)
def auth_status():
    return get_auth_status()

@router.get('/schwab/status', response_model=AuthStatus)
def schwab_auth_status():
    return get_schwab_status()
```

- [ ] **Step 4: Add Schwab sync routes to routes/sync.py**

Replace the full content of `backend/routes/sync.py` with:

```python
from fastapi import APIRouter
from backend.sync import sync_stock_orders, sync_option_orders
from backend.schwab_sync import sync_schwab_orders
from backend.database import (
    get_last_synced, set_last_synced,
    get_schwab_last_synced, set_schwab_last_synced,
)
from backend.models import SyncStatus
from datetime import datetime, timezone

router = APIRouter(prefix='/sync', tags=['sync'])

_sync_state: dict = {'status': 'idle', 'error': None}
_schwab_sync_state: dict = {'status': 'idle', 'error': None}


@router.get('/status', response_model=SyncStatus)
def sync_status():
    return SyncStatus(
        status=_sync_state['status'],
        last_synced=get_last_synced(),
        error=_sync_state['error'],
    )


@router.post('', response_model=SyncStatus)
def trigger_sync():
    _sync_state['status'] = 'syncing'
    _sync_state['error'] = None
    try:
        sync_stock_orders()
        sync_option_orders()
        set_last_synced(datetime.now(timezone.utc).isoformat())
        _sync_state['status'] = 'idle'
    except Exception as e:
        _sync_state['status'] = 'error'
        _sync_state['error'] = str(e)
    return SyncStatus(
        status=_sync_state['status'],
        last_synced=get_last_synced(),
        error=_sync_state['error'],
    )


@router.get('/schwab/status', response_model=SyncStatus)
def schwab_sync_status():
    return SyncStatus(
        status=_schwab_sync_state['status'],
        last_synced=get_schwab_last_synced(),
        error=_schwab_sync_state['error'],
    )


@router.post('/schwab', response_model=SyncStatus)
def trigger_schwab_sync():
    _schwab_sync_state['status'] = 'syncing'
    _schwab_sync_state['error'] = None
    try:
        sync_schwab_orders()
        set_schwab_last_synced(datetime.now(timezone.utc).isoformat())
        _schwab_sync_state['status'] = 'idle'
    except Exception as e:
        _schwab_sync_state['status'] = 'error'
        _schwab_sync_state['error'] = str(e)
    return SyncStatus(
        status=_schwab_sync_state['status'],
        last_synced=get_schwab_last_synced(),
        error=_schwab_sync_state['error'],
    )
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python3 -m pytest backend/tests/test_routes_schwab.py backend/tests/test_routes_sync.py -v
```

Expected: all pass (both new and existing route tests)

- [ ] **Step 6: Run full test suite**

```bash
python3 -m pytest backend/tests/ -v
```

Expected: all pass

- [ ] **Step 7: Commit**

```bash
git add backend/routes/auth.py backend/routes/sync.py backend/tests/test_routes_schwab.py
git commit -m "feat: add Schwab auth and sync routes"
```

---

## Task 8: main.py startup check

**Files:**
- Modify: `backend/main.py`

- [ ] **Step 1: Update main.py to log Schwab auth status**

Replace the full content of `backend/main.py` with:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.auth import router as auth_router
from backend.routes.sync import router as sync_router
from backend.routes.trades import router as trades_router
from backend.database import init_db
from backend.auth import login_from_config
from backend.schwab_auth import get_schwab_status


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # Fatal if DB unavailable — intentionally unguarded

    result = login_from_config()
    if not result.get('authenticated'):
        print()
        print("WARNING: Not authenticated with Robinhood.")
        print("Run this once to set up your session:")
        print("  python3 backend/authenticate.py")
        print()

    schwab_result = get_schwab_status()
    if not schwab_result.get('authenticated'):
        print()
        print("WARNING: Not authenticated with Schwab.")
        print("Run this once to set up your session:")
        print("  python3.11 backend/schwab_authenticate.py")
        print()

    yield


app = FastAPI(title='WashSaleApp', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth_router)
app.include_router(sync_router)
app.include_router(trades_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend.main:app', host='0.0.0.0', port=8000, reload=True)
```

- [ ] **Step 2: Run full test suite to confirm nothing broke**

```bash
python3 -m pytest backend/tests/ -q
```

Expected: all pass

- [ ] **Step 3: Restart backend and verify startup logs**

```bash
python3 -m backend.main
```

Expected output (if Schwab not yet set up):
```
WARNING: Not authenticated with Schwab.
Run this once to set up your session:
  python3.11 backend/schwab_authenticate.py
```

- [ ] **Step 4: Commit**

```bash
git add backend/main.py
git commit -m "feat: log Schwab auth status on backend startup"
```

---

## Task 9: Frontend — api.js + SyncBar + styles

**Files:**
- Modify: `frontend/src/api.js`
- Modify: `frontend/src/components/SyncBar.jsx`
- Modify: `frontend/src/App.css`

- [ ] **Step 1: Add Schwab API functions to api.js**

Replace the full content of `frontend/src/api.js` with:

```javascript
const BASE = 'http://localhost:8000';

export async function getAuthStatus() {
  const res = await fetch(`${BASE}/auth/status`);
  if (!res.ok) throw new Error('Failed to fetch auth status');
  return res.json();
}

export async function getSyncStatus() {
  const res = await fetch(`${BASE}/sync/status`);
  if (!res.ok) throw new Error('Failed to fetch sync status');
  return res.json();
}

export async function triggerSync() {
  const res = await fetch(`${BASE}/sync`, { method: 'POST' });
  if (!res.ok) throw new Error('Sync failed');
  return res.json();
}

export async function getSchwabSyncStatus() {
  const res = await fetch(`${BASE}/sync/schwab/status`);
  if (!res.ok) throw new Error('Failed to fetch Schwab sync status');
  return res.json();
}

export async function triggerSchwabSync() {
  const res = await fetch(`${BASE}/sync/schwab`, { method: 'POST' });
  if (!res.ok) throw new Error('Schwab sync failed');
  return res.json();
}

export async function searchTrades({ symbol, expiry, strike }) {
  const params = new URLSearchParams({ symbol });
  if (expiry) params.set('expiry', expiry);
  if (strike !== undefined && strike !== '') params.set('strike', String(strike));
  const res = await fetch(`${BASE}/trades?${params}`);
  if (!res.ok) throw new Error('Failed to fetch trades');
  return res.json();
}
```

- [ ] **Step 2: Update SyncBar.jsx with two platform rows**

Replace the full content of `frontend/src/components/SyncBar.jsx` with:

```jsx
import { useState, useEffect } from 'react';
import {
  getSyncStatus, triggerSync,
  getSchwabSyncStatus, triggerSchwabSync,
} from '../api';

function PlatformSyncRow({ name, getStatus, triggerSync: doSync }) {
  const [syncState, setSyncState] = useState({ status: 'idle', last_synced: null });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getStatus().then(setSyncState).catch(console.error);
  }, []);

  async function handleSync() {
    setLoading(true);
    setSyncState(s => ({ ...s, status: 'syncing' }));
    try {
      const result = await doSync();
      setSyncState(result);
    } catch (err) {
      setSyncState(s => ({ ...s, status: 'error', error: err.message }));
    } finally {
      setLoading(false);
    }
  }

  const timestampText = syncState.last_synced
    ? `Last synced: ${new Date(syncState.last_synced).toLocaleString()}`
    : 'Never synced';

  return (
    <div className="sync-bar-row">
      <span className="sync-platform">{name}</span>
      <span className="sync-timestamp">
        {syncState.status === 'syncing' ? 'Syncing...' : timestampText}
      </span>
      {syncState.status === 'error' && (
        <span className="sync-error"> — Error: {syncState.error}</span>
      )}
      <button className="sync-button" onClick={handleSync} disabled={loading}>
        {loading ? '⟳ Syncing...' : 'Sync Now'}
      </button>
    </div>
  );
}

export default function SyncBar() {
  return (
    <div className="sync-bar">
      <PlatformSyncRow
        name="Robinhood"
        getStatus={getSyncStatus}
        triggerSync={triggerSync}
      />
      <PlatformSyncRow
        name="Schwab"
        getStatus={getSchwabSyncStatus}
        triggerSync={triggerSchwabSync}
      />
    </div>
  );
}
```

- [ ] **Step 3: Add CSS for the new sync bar layout**

Open `frontend/src/App.css`. Find the existing `.sync-bar` rule and replace the sync-related styles with:

```css
.sync-bar {
  background: #1a1a2e;
  border-bottom: 1px solid #333;
  padding: 0;
}

.sync-bar-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  border-bottom: 1px solid #222;
}

.sync-bar-row:last-child {
  border-bottom: none;
}

.sync-platform {
  font-weight: 600;
  color: #a0a0b0;
  font-size: 0.85rem;
  width: 80px;
  flex-shrink: 0;
}

.sync-timestamp {
  color: #888;
  font-size: 0.85rem;
  flex: 1;
}

.sync-error {
  color: #ff6b6b;
  font-size: 0.85rem;
}

.sync-button {
  background: #4a4a8a;
  color: white;
  border: none;
  padding: 4px 14px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.sync-button:hover:not(:disabled) {
  background: #6a6aaa;
}

.sync-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

- [ ] **Step 4: Verify the frontend builds without errors**

```bash
cd frontend && npm run build 2>&1 | tail -5
```

Expected: `✓ built in ...ms` with no errors

- [ ] **Step 5: Start both servers and verify UI**

```bash
# Terminal 1
python3 -m backend.main

# Terminal 2
cd frontend && npm run dev
```

Open `http://localhost:5173` — verify:
- Two rows in the sync bar: "Robinhood" and "Schwab"
- Each row has its own "Sync Now" button
- Clicking "Sync Now" on Schwab shows "Syncing..." then shows error (expected — no Schwab token yet)
- Robinhood sync still works normally

- [ ] **Step 6: Commit**

```bash
git add frontend/src/api.js frontend/src/components/SyncBar.jsx frontend/src/App.css
git commit -m "feat: add Schwab sync row to SyncBar with independent sync state"
```

---

## After All Tasks: One-Time Schwab Setup

Once implementation is complete, run the auth script to connect your Schwab account:

```bash
python3.11 backend/schwab_authenticate.py
```

This opens a browser → log in → approve → tokens saved to `~/.tokens/schwab_token.json`.

Then click "Sync Now" next to Schwab in the UI — your orders will populate the trades table alongside Robinhood orders.
