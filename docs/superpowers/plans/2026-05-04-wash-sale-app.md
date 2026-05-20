# Wash Sale Prevention App — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-user web app (FastAPI + React) that syncs Robinhood trade history locally and lets the user look up all trades for a symbol in the past 30 days to prevent wash sale violations.

**Architecture:** Python FastAPI backend on port 8000 handles Robinhood authentication via `robin_stocks`, syncs all stock and options trades to a local SQLite database, and exposes REST endpoints. React + Vite frontend on port 5173 provides a sync bar, search filters, and a color-coded results table.

**Tech Stack:** Python 3.11+, FastAPI, uvicorn, robin_stocks, PyYAML, SQLite (stdlib), pytest, httpx; React 18, Vite.

---

## File Map

### Backend
| File | Responsibility |
|---|---|
| `config.yaml` | Robinhood credentials (project root, gitignored) |
| `backend/main.py` | FastAPI app, CORS, router registration, startup |
| `backend/config.py` | Read/write `config.yaml` |
| `backend/database.py` | SQLite connection, schema, upsert, search |
| `backend/auth.py` | `robin_stocks` login, session check |
| `backend/sync.py` | Fetch stock + option orders, store to SQLite |
| `backend/models.py` | Pydantic response models |
| `backend/routes/auth.py` | `GET /auth/status` |
| `backend/routes/sync.py` | `POST /sync`, `GET /sync/status` |
| `backend/routes/trades.py` | `GET /trades?symbol=&expiry=&strike=` |
| `backend/tests/test_config.py` | Config module tests |
| `backend/tests/test_database.py` | Database module tests |
| `backend/tests/test_auth.py` | Auth module tests |
| `backend/tests/test_sync.py` | Sync module tests |
| `backend/tests/test_routes_auth.py` | Auth route tests |
| `backend/tests/test_routes_sync.py` | Sync route tests |
| `backend/tests/test_routes_trades.py` | Trades route tests |

### Frontend
| File | Responsibility |
|---|---|
| `frontend/src/main.jsx` | React entry point |
| `frontend/src/App.jsx` | Root component, layout, state |
| `frontend/src/App.css` | All styles, color coding |
| `frontend/src/api.js` | Fetch wrappers for backend endpoints |
| `frontend/src/components/SyncBar.jsx` | Sync timestamp + Sync Now button |
| `frontend/src/components/SearchFilters.jsx` | Symbol / expiry / strike inputs |
| `frontend/src/components/TradesTable.jsx` | Results table, color coding |

---

## Task 1: Project Scaffold

**Files:**
- Create: `config.yaml`
- Create: `backend/requirements.txt`
- Create: `backend/__init__.py`, `backend/tests/__init__.py`, `backend/routes/__init__.py`
- Create: `.gitignore`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p backend/tests backend/routes frontend
touch backend/__init__.py backend/tests/__init__.py backend/routes/__init__.py
```

- [ ] **Step 2: Create `backend/requirements.txt`**

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
robin-stocks==3.0.6
PyYAML==6.0.1
pytest==8.2.0
httpx==0.27.0
```

- [ ] **Step 3: Create `config.yaml` template at project root**

```yaml
robinhood:
  username: your_email@example.com
  password: your_password
```

- [ ] **Step 4: Create `.gitignore`**

```
config.yaml
*.pickle
__pycache__/
*.pyc
.pytest_cache/
backend/db.sqlite
node_modules/
frontend/dist/
.env
```

- [ ] **Step 5: Install backend dependencies**

```bash
pip install -r backend/requirements.txt
```

Expected: All packages install without errors.

- [ ] **Step 6: Scaffold frontend**

```bash
cd frontend && npm create vite@latest . -- --template react && npm install
```

Expected: `frontend/src/` created with React boilerplate.

- [ ] **Step 7: Commit**

```bash
git init
git add backend/requirements.txt backend/__init__.py backend/tests/__init__.py backend/routes/__init__.py .gitignore
git commit -m "feat: project scaffold"
```

---

## Task 2: Config Module

**Files:**
- Create: `backend/config.py`
- Create: `backend/tests/test_config.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_config.py`:
```python
import pytest
import tempfile
import os
import yaml
from backend.config import load_config, save_config

def test_load_config_reads_yaml():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({'robinhood': {'username': 'test@test.com', 'password': 'secret'}}, f)
        path = f.name
    try:
        config = load_config(path)
        assert config['robinhood']['username'] == 'test@test.com'
        assert config['robinhood']['password'] == 'secret'
    finally:
        os.unlink(path)

def test_load_config_raises_if_missing():
    with pytest.raises(FileNotFoundError):
        load_config('/nonexistent/path/config.yaml')

def test_save_config_writes_yaml():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        path = f.name
    try:
        config = {'robinhood': {'username': 'user@test.com', 'password': 'pw'}}
        save_config(config, path)
        with open(path) as f:
            loaded = yaml.safe_load(f)
        assert loaded['robinhood']['username'] == 'user@test.com'
    finally:
        os.unlink(path)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest backend/tests/test_config.py -v
```

Expected: `ImportError: cannot import name 'load_config'`

- [ ] **Step 3: Implement `backend/config.py`**

```python
import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')

def load_config(path: str = CONFIG_PATH) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path) as f:
        return yaml.safe_load(f)

def save_config(config: dict, path: str = CONFIG_PATH) -> None:
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest backend/tests/test_config.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/config.py backend/tests/test_config.py
git commit -m "feat: config read/write module"
```

---

## Task 3: Database Module

**Files:**
- Create: `backend/database.py`
- Create: `backend/tests/test_database.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_database.py`:
```python
import pytest
from backend.database import init_db, upsert_trade, get_connection, \
    get_last_synced, set_last_synced, search_trades

STOCK_TRADE = {
    'id': 'order-1', 'symbol': 'META', 'platform': 'robinhood',
    'trade_type': 'stock', 'option_type': None, 'strategy': None,
    'side': 'buy', 'expiration_date': None, 'strike_price': None,
    'trade_price': 500.00, 'quantity': 10.0, 'status': 'closed',
    'executed_at': '2026-04-20T10:00:00+00:00',
    'synced_at': '2026-05-04T12:00:00+00:00',
}

OPTION_TRADE = {
    'id': 'opt-1', 'symbol': 'META', 'platform': 'robinhood',
    'trade_type': 'option', 'option_type': 'call', 'strategy': 'single',
    'side': 'buy', 'expiration_date': '2026-06-20', 'strike_price': 600.0,
    'trade_price': 5.50, 'quantity': 1.0, 'status': 'open',
    'executed_at': '2026-04-20T14:00:00+00:00',
    'synced_at': '2026-05-04T12:00:00+00:00',
}

def test_init_db_creates_trades_table(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='trades'"
        ).fetchone()
    assert row is not None

def test_upsert_trade_inserts_stock(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    upsert_trade(STOCK_TRADE, db_path)
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM trades WHERE id = 'order-1'").fetchone()
    assert row['symbol'] == 'META'
    assert row['trade_type'] == 'stock'
    assert row['option_type'] is None
    assert row['strategy'] is None

def test_upsert_trade_no_duplicates_on_resync(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    upsert_trade(STOCK_TRADE, db_path)
    updated = {**STOCK_TRADE, 'status': 'open'}
    upsert_trade(updated, db_path)
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM trades WHERE id = 'order-1'").fetchall()
    assert len(rows) == 1
    assert rows[0]['status'] == 'open'

def test_upsert_trade_stores_option_fields(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    upsert_trade(OPTION_TRADE, db_path)
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM trades WHERE id = 'opt-1'").fetchone()
    assert row['option_type'] == 'call'
    assert row['strike_price'] == 600.0
    assert row['expiration_date'] == '2026-06-20'
    assert row['strategy'] == 'single'

def test_sync_meta_get_set(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    assert get_last_synced(db_path) is None
    set_last_synced('2026-05-04T12:00:00+00:00', db_path)
    assert get_last_synced(db_path) == '2026-05-04T12:00:00+00:00'
    set_last_synced('2026-05-04T13:00:00+00:00', db_path)
    assert get_last_synced(db_path) == '2026-05-04T13:00:00+00:00'

def test_search_trades_filters_by_symbol(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    upsert_trade(OPTION_TRADE, db_path)
    aapl_trade = {**STOCK_TRADE, 'id': 'aapl-1', 'symbol': 'AAPL'}
    upsert_trade(aapl_trade, db_path)
    results = search_trades('META', None, None, db_path)
    assert len(results) == 1
    assert results[0]['symbol'] == 'META'

def test_search_trades_returns_empty_for_unknown_symbol(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    results = search_trades('ZZZZ', None, None, db_path)
    assert results == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest backend/tests/test_database.py -v
```

Expected: `ImportError: cannot import name 'init_db'`

- [ ] **Step 3: Implement `backend/database.py`**

```python
import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), 'db.sqlite')

@contextmanager
def get_connection(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db(db_path: str = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                platform TEXT NOT NULL DEFAULT 'robinhood',
                trade_type TEXT NOT NULL,
                option_type TEXT,
                strategy TEXT,
                side TEXT NOT NULL,
                expiration_date TEXT,
                strike_price REAL,
                trade_price REAL NOT NULL,
                quantity REAL NOT NULL,
                status TEXT NOT NULL,
                executed_at TEXT NOT NULL,
                synced_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

def upsert_trade(trade: dict, db_path: str = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO trades (
                id, symbol, platform, trade_type, option_type, strategy,
                side, expiration_date, strike_price, trade_price,
                quantity, status, executed_at, synced_at
            ) VALUES (
                :id, :symbol, :platform, :trade_type, :option_type, :strategy,
                :side, :expiration_date, :strike_price, :trade_price,
                :quantity, :status, :executed_at, :synced_at
            )
            ON CONFLICT(id) DO UPDATE SET
                status=excluded.status,
                synced_at=excluded.synced_at,
                trade_price=excluded.trade_price,
                quantity=excluded.quantity
        """, trade)

def get_last_synced(db_path: str = DB_PATH) -> str | None:
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT value FROM sync_meta WHERE key = 'last_synced'"
        ).fetchone()
        return row['value'] if row else None

def set_last_synced(timestamp: str, db_path: str = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO sync_meta (key, value) VALUES ('last_synced', ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (timestamp,))

def search_trades(
    symbol: str,
    expiry: str | None,
    strike: float | None,
    db_path: str = DB_PATH,
) -> list[dict]:
    query = """
        SELECT * FROM trades
        WHERE symbol = ?
        AND executed_at >= datetime('now', '-30 days')
    """
    params: list = [symbol.upper()]
    if expiry:
        query += " AND expiration_date = ?"
        params.append(expiry)
    if strike is not None:
        query += " AND strike_price = ?"
        params.append(strike)
    query += " ORDER BY executed_at DESC"
    with get_connection(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest backend/tests/test_database.py -v
```

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/database.py backend/tests/test_database.py
git commit -m "feat: SQLite database module with trades schema and search"
```

---

## Task 4: Auth Module

**Files:**
- Create: `backend/auth.py`
- Create: `backend/tests/test_auth.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_auth.py`:
```python
from unittest.mock import patch
from backend.auth import login, get_auth_status

def test_login_success():
    with patch('backend.auth.r.login') as mock_login, \
         patch('backend.auth.r.account.load_account_profile') as mock_profile:
        mock_login.return_value = {'access_token': 'fake-token'}
        mock_profile.return_value = {'username': 'test@test.com'}
        result = login('test@test.com', 'pass')
    assert result['authenticated'] is True
    mock_login.assert_called_once_with(
        username='test@test.com',
        password='pass',
        store_session=True,
        by_sms=True,
    )

def test_login_failure_returns_error():
    with patch('backend.auth.r.login') as mock_login:
        mock_login.side_effect = Exception("Invalid credentials")
        result = login('bad@test.com', 'wrong')
    assert result['authenticated'] is False
    assert 'error' in result

def test_get_auth_status_authenticated():
    with patch('backend.auth.r.account.load_account_profile') as mock_profile:
        mock_profile.return_value = {'username': 'test@test.com'}
        status = get_auth_status()
    assert status['authenticated'] is True

def test_get_auth_status_unauthenticated():
    with patch('backend.auth.r.account.load_account_profile') as mock_profile:
        mock_profile.side_effect = Exception("Not logged in")
        status = get_auth_status()
    assert status['authenticated'] is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest backend/tests/test_auth.py -v
```

Expected: `ImportError: cannot import name 'login'`

- [ ] **Step 3: Implement `backend/auth.py`**

```python
import robin_stocks.robinhood as r
from backend.config import load_config

def login(username: str, password: str) -> dict:
    """Login to Robinhood. robin_stocks prompts for MFA on the CLI automatically."""
    try:
        r.login(username=username, password=password, store_session=True, by_sms=True)
        r.account.load_account_profile()
        return {'authenticated': True}
    except Exception as e:
        return {'authenticated': False, 'error': str(e)}

def login_from_config(config_path: str = None) -> dict:
    kwargs = {'path': config_path} if config_path else {}
    config = load_config(**kwargs)
    creds = config.get('robinhood', {})
    return login(
        username=creds.get('username', ''),
        password=creds.get('password', ''),
    )

def get_auth_status() -> dict:
    try:
        r.account.load_account_profile()
        return {'authenticated': True}
    except Exception:
        return {'authenticated': False}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest backend/tests/test_auth.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/auth.py backend/tests/test_auth.py
git commit -m "feat: Robinhood auth module"
```

---

## Task 5: Sync — Stock Orders

**Files:**
- Create: `backend/sync.py`
- Create: `backend/tests/test_sync.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_sync.py`:
```python
from unittest.mock import patch
from backend.sync import sync_stock_orders
from backend.database import init_db, get_connection

MOCK_STOCK_ORDERS = [
    {
        'id': 'stock-1',
        'instrument': 'https://api.robinhood.com/instruments/abc/',
        'side': 'buy',
        'average_price': '500.00',
        'quantity': '10.00000',
        'state': 'filled',
        'last_transaction_at': '2026-04-20T10:00:00Z',
    },
    {
        'id': 'stock-2',
        'instrument': 'https://api.robinhood.com/instruments/abc/',
        'side': 'sell',
        'average_price': '510.00',
        'quantity': '5.00000',
        'state': 'cancelled',
        'last_transaction_at': '2026-04-21T11:00:00Z',
    },
]

MOCK_INSTRUMENT = {'symbol': 'META'}

def test_sync_stock_orders_stores_trades(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    with patch('backend.sync.r.orders.get_all_stock_orders', return_value=MOCK_STOCK_ORDERS), \
         patch('backend.sync.r.helper.request_get', return_value=MOCK_INSTRUMENT):
        count = sync_stock_orders(db_path=db_path)
    assert count == 2
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM trades WHERE trade_type='stock'").fetchall()
    assert len(rows) == 2
    assert rows[0]['symbol'] == 'META'
    assert rows[0]['option_type'] is None
    assert rows[0]['strategy'] is None

def test_sync_stock_orders_maps_status(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    with patch('backend.sync.r.orders.get_all_stock_orders', return_value=MOCK_STOCK_ORDERS), \
         patch('backend.sync.r.helper.request_get', return_value=MOCK_INSTRUMENT):
        sync_stock_orders(db_path=db_path)
    with get_connection(db_path) as conn:
        filled = conn.execute("SELECT status FROM trades WHERE id='stock-1'").fetchone()
        cancelled = conn.execute("SELECT status FROM trades WHERE id='stock-2'").fetchone()
    assert filled['status'] == 'closed'
    assert cancelled['status'] == 'closed'

def test_sync_stock_orders_no_duplicates(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    with patch('backend.sync.r.orders.get_all_stock_orders', return_value=MOCK_STOCK_ORDERS), \
         patch('backend.sync.r.helper.request_get', return_value=MOCK_INSTRUMENT):
        sync_stock_orders(db_path=db_path)
        sync_stock_orders(db_path=db_path)
    with get_connection(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
    assert count == 2
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest backend/tests/test_sync.py -v
```

Expected: `ImportError: cannot import name 'sync_stock_orders'`

- [ ] **Step 3: Create `backend/sync.py`**

```python
import robin_stocks.robinhood as r
from datetime import datetime, timezone
from backend.database import upsert_trade

STATUS_MAP = {
    'filled': 'closed',
    'cancelled': 'closed',
    'rejected': 'closed',
    'confirmed': 'open',
    'unconfirmed': 'open',
    'partially_filled': 'open',
}

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def sync_stock_orders(db_path: str = None) -> int:
    """Fetch all stock orders from Robinhood and upsert into SQLite."""
    kwargs = {'db_path': db_path} if db_path else {}
    orders = r.orders.get_all_stock_orders()
    count = 0
    for order in orders:
        if not order.get('average_price') or not order.get('last_transaction_at'):
            continue
        instrument = r.helper.request_get(order['instrument'])
        trade = {
            'id': order['id'],
            'symbol': instrument.get('symbol', '').upper(),
            'platform': 'robinhood',
            'trade_type': 'stock',
            'option_type': None,
            'strategy': None,
            'side': order['side'],
            'expiration_date': None,
            'strike_price': None,
            'trade_price': float(order['average_price']),
            'quantity': float(order['quantity']),
            'status': STATUS_MAP.get(order['state'], 'closed'),
            'executed_at': order['last_transaction_at'],
            'synced_at': _now_iso(),
        }
        upsert_trade(trade, **kwargs)
        count += 1
    return count
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest backend/tests/test_sync.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/sync.py backend/tests/test_sync.py
git commit -m "feat: sync stock orders from Robinhood"
```

---

## Task 6: Sync — Option Orders

**Files:**
- Modify: `backend/sync.py`
- Modify: `backend/tests/test_sync.py`

- [ ] **Step 1: Write the failing tests**

Add to the bottom of `backend/tests/test_sync.py`:
```python
from backend.sync import sync_option_orders

MOCK_OPTION_ORDERS = [
    {
        'id': 'opt-order-1',
        'chain_symbol': 'META',
        'price': '5.50',
        'quantity': '1.00000',
        'state': 'filled',
        'opening_strategy': 'long_call',
        'closing_strategy': None,
        'created_at': '2026-04-15T14:00:00Z',
        'legs': [
            {
                'option': 'https://api.robinhood.com/options/instruments/leg-1/',
                'side': 'buy',
                'position_effect': 'open',
                'ratio_quantity': '1',
            }
        ],
    },
    {
        'id': 'opt-order-2',
        'chain_symbol': 'META',
        'price': '2.00',
        'quantity': '1.00000',
        'state': 'filled',
        'opening_strategy': 'iron_condor',
        'closing_strategy': None,
        'created_at': '2026-04-16T14:00:00Z',
        'legs': [
            {'option': 'https://api.robinhood.com/options/instruments/leg-2/',
             'side': 'sell', 'position_effect': 'open', 'ratio_quantity': '1'},
            {'option': 'https://api.robinhood.com/options/instruments/leg-3/',
             'side': 'buy', 'position_effect': 'open', 'ratio_quantity': '1'},
            {'option': 'https://api.robinhood.com/options/instruments/leg-4/',
             'side': 'sell', 'position_effect': 'open', 'ratio_quantity': '1'},
            {'option': 'https://api.robinhood.com/options/instruments/leg-5/',
             'side': 'buy', 'position_effect': 'open', 'ratio_quantity': '1'},
        ],
    },
]

_INSTRUMENTS = {
    'https://api.robinhood.com/options/instruments/leg-1/':
        {'expiration_date': '2026-06-20', 'strike_price': '600.0000', 'type': 'call'},
    'https://api.robinhood.com/options/instruments/leg-2/':
        {'expiration_date': '2026-06-20', 'strike_price': '610.0000', 'type': 'call'},
    'https://api.robinhood.com/options/instruments/leg-3/':
        {'expiration_date': '2026-06-20', 'strike_price': '620.0000', 'type': 'call'},
    'https://api.robinhood.com/options/instruments/leg-4/':
        {'expiration_date': '2026-06-20', 'strike_price': '580.0000', 'type': 'put'},
    'https://api.robinhood.com/options/instruments/leg-5/':
        {'expiration_date': '2026-06-20', 'strike_price': '570.0000', 'type': 'put'},
}

def test_sync_option_orders_one_row_per_leg(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    with patch('backend.sync.r.orders.get_all_option_orders', return_value=MOCK_OPTION_ORDERS), \
         patch('backend.sync.r.helper.request_get', side_effect=lambda url: _INSTRUMENTS[url]):
        count = sync_option_orders(db_path=db_path)
    # 1 leg (single call) + 4 legs (iron condor) = 5
    assert count == 5
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM trades WHERE trade_type='option'").fetchall()
    assert len(rows) == 5

def test_sync_option_orders_maps_strategy(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    with patch('backend.sync.r.orders.get_all_option_orders', return_value=MOCK_OPTION_ORDERS), \
         patch('backend.sync.r.helper.request_get', side_effect=lambda url: _INSTRUMENTS[url]):
        sync_option_orders(db_path=db_path)
    with get_connection(db_path) as conn:
        single = conn.execute(
            "SELECT strategy FROM trades WHERE id='opt-order-1-leg-0'"
        ).fetchone()
        condor = conn.execute(
            "SELECT strategy FROM trades WHERE id='opt-order-2-leg-0'"
        ).fetchone()
    assert single['strategy'] == 'single'
    assert condor['strategy'] == 'iron_condor'

def test_sync_option_orders_sets_option_type_and_strike(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    with patch('backend.sync.r.orders.get_all_option_orders', return_value=MOCK_OPTION_ORDERS), \
         patch('backend.sync.r.helper.request_get', side_effect=lambda url: _INSTRUMENTS[url]):
        sync_option_orders(db_path=db_path)
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM trades WHERE id='opt-order-1-leg-0'").fetchone()
    assert row['option_type'] == 'call'
    assert row['strike_price'] == 600.0
    assert row['expiration_date'] == '2026-06-20'
```

- [ ] **Step 2: Run new tests to verify they fail**

```bash
python -m pytest backend/tests/test_sync.py::test_sync_option_orders_one_row_per_leg -v
```

Expected: `ImportError: cannot import name 'sync_option_orders'`

- [ ] **Step 3: Add option sync to `backend/sync.py`**

Add after `sync_stock_orders`:
```python
STRATEGY_MAP = {
    'long_call': 'single',
    'short_call': 'single',
    'long_put': 'single',
    'short_put': 'single',
    'long_call_spread': 'call_spread',
    'short_call_spread': 'call_spread',
    'long_put_spread': 'put_spread',
    'short_put_spread': 'put_spread',
    'iron_condor': 'iron_condor',
    'iron_butterfly': 'iron_condor',
}

def sync_option_orders(db_path: str = None) -> int:
    """Fetch all option orders from Robinhood, storing one row per leg."""
    kwargs = {'db_path': db_path} if db_path else {}
    orders = r.orders.get_all_option_orders()
    count = 0
    for order in orders:
        if not order.get('created_at'):
            continue
        raw_strategy = order.get('opening_strategy') or order.get('closing_strategy') or ''
        strategy = STRATEGY_MAP.get(raw_strategy, 'single')
        for i, leg in enumerate(order.get('legs', [])):
            instrument = r.helper.request_get(leg['option'])
            trade = {
                'id': f"{order['id']}-leg-{i}",
                'symbol': order['chain_symbol'].upper(),
                'platform': 'robinhood',
                'trade_type': 'option',
                'option_type': instrument.get('type'),
                'strategy': strategy,
                'side': leg['side'],
                'expiration_date': instrument.get('expiration_date'),
                'strike_price': float(instrument['strike_price']) if instrument.get('strike_price') else None,
                'trade_price': float(order['price']) if order.get('price') else 0.0,
                'quantity': float(order['quantity']),
                'status': STATUS_MAP.get(order['state'], 'closed'),
                'executed_at': order['created_at'],
                'synced_at': _now_iso(),
            }
            upsert_trade(trade, **kwargs)
            count += 1
    return count
```

- [ ] **Step 4: Run all sync tests to verify they pass**

```bash
python -m pytest backend/tests/test_sync.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/sync.py backend/tests/test_sync.py
git commit -m "feat: sync option orders from Robinhood (one row per leg)"
```

---

## Task 7: FastAPI App + Auth Endpoint

**Files:**
- Create: `backend/models.py`
- Create: `backend/routes/auth.py`
- Create: `backend/main.py`
- Create: `backend/tests/test_routes_auth.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_routes_auth.py`:
```python
from unittest.mock import patch
from fastapi.testclient import TestClient

def get_client():
    with patch('backend.main.login_from_config'):
        from backend.main import app
        return TestClient(app)

def test_auth_status_authenticated():
    client = get_client()
    with patch('backend.auth.r.account.load_account_profile', return_value={'username': 'u'}):
        response = client.get('/auth/status')
    assert response.status_code == 200
    assert response.json()['authenticated'] is True

def test_auth_status_unauthenticated():
    client = get_client()
    with patch('backend.auth.r.account.load_account_profile', side_effect=Exception("not logged in")):
        response = client.get('/auth/status')
    assert response.status_code == 200
    assert response.json()['authenticated'] is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest backend/tests/test_routes_auth.py -v
```

Expected: `ImportError: cannot import name 'app'`

- [ ] **Step 3: Create `backend/models.py`**

```python
from pydantic import BaseModel
from typing import Optional

class AuthStatus(BaseModel):
    authenticated: bool
    error: Optional[str] = None

class SyncStatus(BaseModel):
    status: str
    last_synced: Optional[str] = None
    error: Optional[str] = None

class Trade(BaseModel):
    id: str
    symbol: str
    platform: str
    trade_type: str
    option_type: Optional[str] = None
    strategy: Optional[str] = None
    side: str
    expiration_date: Optional[str] = None
    strike_price: Optional[float] = None
    trade_price: float
    quantity: float
    status: str
    executed_at: str
    synced_at: str
```

- [ ] **Step 4: Create `backend/routes/auth.py`**

```python
from fastapi import APIRouter
from backend.auth import get_auth_status
from backend.models import AuthStatus

router = APIRouter(prefix='/auth', tags=['auth'])

@router.get('/status', response_model=AuthStatus)
def auth_status():
    return get_auth_status()
```

- [ ] **Step 5: Create `backend/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.auth import router as auth_router
from backend.routes.sync import router as sync_router
from backend.routes.trades import router as trades_router
from backend.database import init_db
from backend.auth import login_from_config

app = FastAPI(title='WashSaleApp')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth_router)
app.include_router(sync_router)
app.include_router(trades_router)

@app.on_event('startup')
def startup():
    init_db()
    try:
        login_from_config()
    except Exception as e:
        print(f"Warning: Could not auto-login on startup: {e}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend.main:app', host='0.0.0.0', port=8000, reload=True)
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
python -m pytest backend/tests/test_routes_auth.py -v
```

Expected: 2 passed.

- [ ] **Step 7: Commit**

```bash
git add backend/main.py backend/models.py backend/routes/auth.py backend/tests/test_routes_auth.py
git commit -m "feat: FastAPI app with CORS and auth status endpoint"
```

---

## Task 8: Sync Endpoints

**Files:**
- Create: `backend/routes/sync.py`
- Create: `backend/tests/test_routes_sync.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_routes_sync.py`:
```python
from unittest.mock import patch
from fastapi.testclient import TestClient

def get_client():
    with patch('backend.main.login_from_config'):
        from backend.main import app
        return TestClient(app)

def test_sync_status_never_synced():
    client = get_client()
    with patch('backend.routes.sync.get_last_synced', return_value=None):
        response = client.get('/sync/status')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'idle'
    assert data['last_synced'] is None

def test_sync_status_shows_timestamp():
    client = get_client()
    with patch('backend.routes.sync.get_last_synced', return_value='2026-05-04T12:00:00+00:00'):
        response = client.get('/sync/status')
    assert response.json()['last_synced'] == '2026-05-04T12:00:00+00:00'

def test_post_sync_calls_both_syncs():
    client = get_client()
    with patch('backend.routes.sync.sync_stock_orders', return_value=10) as ms, \
         patch('backend.routes.sync.sync_option_orders', return_value=5) as mo, \
         patch('backend.routes.sync.set_last_synced') as mset, \
         patch('backend.routes.sync.get_last_synced', return_value='2026-05-04T12:00:00+00:00'):
        response = client.post('/sync')
    assert response.status_code == 200
    assert response.json()['status'] == 'idle'
    ms.assert_called_once()
    mo.assert_called_once()
    mset.assert_called_once()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest backend/tests/test_routes_sync.py -v
```

Expected: 404 errors (routes not registered yet).

- [ ] **Step 3: Create `backend/routes/sync.py`**

```python
from fastapi import APIRouter
from backend.sync import sync_stock_orders, sync_option_orders
from backend.database import get_last_synced, set_last_synced
from backend.models import SyncStatus
from datetime import datetime, timezone

router = APIRouter(prefix='/sync', tags=['sync'])

_sync_state: dict = {'status': 'idle', 'error': None}

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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest backend/tests/test_routes_sync.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/routes/sync.py backend/tests/test_routes_sync.py
git commit -m "feat: sync status and trigger endpoints"
```

---

## Task 9: Trades Search Endpoint

**Files:**
- Create: `backend/routes/trades.py`
- Create: `backend/tests/test_routes_trades.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_routes_trades.py`:
```python
from unittest.mock import patch
from fastapi.testclient import TestClient

def get_client():
    with patch('backend.main.login_from_config'):
        from backend.main import app
        return TestClient(app)

MOCK_TRADE = {
    'id': 'opt-1', 'symbol': 'META', 'platform': 'robinhood',
    'trade_type': 'option', 'option_type': 'call', 'strategy': 'single',
    'side': 'buy', 'expiration_date': '2026-06-20', 'strike_price': 600.0,
    'trade_price': 5.50, 'quantity': 1.0, 'status': 'open',
    'executed_at': '2026-04-20T10:00:00Z', 'synced_at': '2026-05-04T12:00:00Z',
}

def test_get_trades_requires_symbol():
    client = get_client()
    response = client.get('/trades')
    assert response.status_code == 422

def test_get_trades_returns_results():
    client = get_client()
    with patch('backend.routes.trades.search_trades', return_value=[MOCK_TRADE]):
        response = client.get('/trades?symbol=META')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['symbol'] == 'META'

def test_get_trades_passes_all_filters():
    client = get_client()
    with patch('backend.routes.trades.search_trades', return_value=[]) as mock_search:
        client.get('/trades?symbol=META&expiry=2026-06-20&strike=600.0')
    mock_search.assert_called_once_with(
        symbol='META', expiry='2026-06-20', strike=600.0
    )

def test_get_trades_empty_result():
    client = get_client()
    with patch('backend.routes.trades.search_trades', return_value=[]):
        response = client.get('/trades?symbol=ZZZZ')
    assert response.status_code == 200
    assert response.json() == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest backend/tests/test_routes_trades.py -v
```

Expected: 404 errors.

- [ ] **Step 3: Create `backend/routes/trades.py`**

```python
from fastapi import APIRouter, Query
from typing import Optional, List
from backend.database import search_trades
from backend.models import Trade

router = APIRouter(prefix='/trades', tags=['trades'])

@router.get('', response_model=List[Trade])
def get_trades(
    symbol: str = Query(..., description="Ticker symbol e.g. META"),
    expiry: Optional[str] = Query(None, description="Expiration date YYYY-MM-DD"),
    strike: Optional[float] = Query(None, description="Strike price"),
):
    return search_trades(symbol=symbol, expiry=expiry, strike=strike)
```

- [ ] **Step 4: Run all backend tests**

```bash
python -m pytest backend/tests/ -v
```

Expected: All tests pass (16+ tests).

- [ ] **Step 5: Manual smoke test**

```bash
python -m backend.main &
sleep 2
curl -s http://localhost:8000/auth/status | python3 -m json.tool
curl -s http://localhost:8000/sync/status | python3 -m json.tool
curl -s "http://localhost:8000/trades?symbol=META" | python3 -m json.tool
kill %1
```

Expected: All three return valid JSON. Trades will be `[]` until a real sync runs.

- [ ] **Step 6: Commit**

```bash
git add backend/routes/trades.py backend/tests/test_routes_trades.py
git commit -m "feat: trades search endpoint with symbol/expiry/strike filters"
```

---

## Task 10: Frontend — API Client

**Files:**
- Create: `frontend/src/api.js`

- [ ] **Step 1: Remove Vite boilerplate**

Delete `frontend/src/App.css` content (we'll replace it in Task 14), clear `frontend/src/App.jsx` to a minimal placeholder:

```jsx
export default function App() {
  return <div>Loading...</div>;
}
```

- [ ] **Step 2: Create `frontend/src/api.js`**

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

export async function searchTrades({ symbol, expiry, strike }) {
  const params = new URLSearchParams({ symbol });
  if (expiry) params.set('expiry', expiry);
  if (strike !== undefined && strike !== '') params.set('strike', String(strike));
  const res = await fetch(`${BASE}/trades?${params}`);
  if (!res.ok) throw new Error('Failed to fetch trades');
  return res.json();
}
```

- [ ] **Step 3: Verify frontend builds without errors**

```bash
cd frontend && npm run build 2>&1 | tail -5
```

Expected: `✓ built in Xs` with no errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/api.js frontend/src/App.jsx
git commit -m "feat: frontend API client"
```

---

## Task 11: SyncBar Component

**Files:**
- Create: `frontend/src/components/SyncBar.jsx`

- [ ] **Step 1: Create `frontend/src/components/SyncBar.jsx`**

```jsx
import { useState, useEffect } from 'react';
import { getSyncStatus, triggerSync } from '../api';

export default function SyncBar() {
  const [syncState, setSyncState] = useState({ status: 'idle', last_synced: null });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getSyncStatus().then(setSyncState).catch(console.error);
  }, []);

  async function handleSync() {
    setLoading(true);
    setSyncState(s => ({ ...s, status: 'syncing' }));
    try {
      const result = await triggerSync();
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
    <div className="sync-bar">
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
```

- [ ] **Step 2: Add SyncBar to App.jsx temporarily and verify in browser**

Start backend and frontend, open `http://localhost:5173`, confirm SyncBar renders with timestamp and button.

```bash
# Terminal 1: python -m backend.main
# Terminal 2: cd frontend && npm run dev
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/SyncBar.jsx
git commit -m "feat: SyncBar component"
```

---

## Task 12: SearchFilters Component

**Files:**
- Create: `frontend/src/components/SearchFilters.jsx`

- [ ] **Step 1: Create `frontend/src/components/SearchFilters.jsx`**

```jsx
import { useState } from 'react';

export default function SearchFilters({ onSearch }) {
  const [symbol, setSymbol] = useState('');
  const [expiry, setExpiry] = useState('');
  const [strike, setStrike] = useState('');

  function handleSubmit(e) {
    e.preventDefault();
    if (!symbol.trim()) return;
    onSearch({
      symbol: symbol.trim().toUpperCase(),
      expiry: expiry || undefined,
      strike: strike !== '' ? parseFloat(strike) : undefined,
    });
  }

  return (
    <form className="search-filters" onSubmit={handleSubmit}>
      <label className="filter-group">
        <span>Symbol *</span>
        <input
          type="text"
          value={symbol}
          onChange={e => setSymbol(e.target.value)}
          placeholder="e.g. META"
          required
        />
      </label>
      <label className="filter-group">
        <span>Expiry</span>
        <input
          type="date"
          value={expiry}
          onChange={e => setExpiry(e.target.value)}
        />
      </label>
      <label className="filter-group">
        <span>Strike</span>
        <input
          type="number"
          value={strike}
          onChange={e => setStrike(e.target.value)}
          placeholder="e.g. 600"
          step="0.5"
          min="0"
        />
      </label>
      <button type="submit">Search</button>
    </form>
  );
}
```

- [ ] **Step 2: Verify in browser**

Add `<SearchFilters onSearch={console.log} />` to `App.jsx`, confirm form renders and `console.log` fires with `{ symbol: 'META', expiry: undefined, strike: undefined }` shape on submit.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/SearchFilters.jsx
git commit -m "feat: SearchFilters component"
```

---

## Task 13: TradesTable Component

**Files:**
- Create: `frontend/src/components/TradesTable.jsx`

- [ ] **Step 1: Create `frontend/src/components/TradesTable.jsx`**

```jsx
export default function TradesTable({ trades, symbol }) {
  if (!symbol) return null;

  if (trades.length === 0) {
    return (
      <div className="trades-empty">
        No trades found for <strong>{symbol}</strong> in the last 30 days.
      </div>
    );
  }

  return (
    <div className="trades-section">
      <p className="trades-count">
        {trades.length} trade{trades.length !== 1 ? 's' : ''} in the last 30 days
      </p>
      <div className="table-scroll">
        <table className="trades-table">
          <thead>
            <tr>
              <th>Symbol</th><th>Platform</th><th>Trade Type</th>
              <th>Option Type</th><th>Strategy</th><th>Side</th>
              <th>Expiry</th><th>Strike</th><th>Trade Price</th>
              <th>Qty</th><th>Status</th><th>Date</th>
            </tr>
          </thead>
          <tbody>
            {trades.map(trade => (
              <tr key={trade.id} className={`row-status-${trade.status}`}>
                <td>{trade.symbol}</td>
                <td>{trade.platform}</td>
                <td>{trade.trade_type}</td>
                <td>
                  {trade.option_type
                    ? <span className={`badge badge-${trade.option_type}`}>{trade.option_type}</span>
                    : <span className="badge badge-na">N/A</span>}
                </td>
                <td>
                  {trade.strategy
                    ? <span className={`badge badge-strategy badge-${trade.strategy.replace('_', '-')}`}>
                        {trade.strategy.replace(/_/g, ' ')}
                      </span>
                    : '—'}
                </td>
                <td className={`side-${trade.side}`}>{trade.side}</td>
                <td>{trade.expiration_date ?? '—'}</td>
                <td>{trade.strike_price != null ? `$${trade.strike_price}` : '—'}</td>
                <td>${trade.trade_price?.toFixed(2)}</td>
                <td>{trade.quantity}</td>
                <td>
                  <span className={`badge badge-status-${trade.status}`}>{trade.status}</span>
                </td>
                <td>{new Date(trade.executed_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/TradesTable.jsx
git commit -m "feat: TradesTable component with color coding"
```

---

## Task 14: App Integration + Styles

**Files:**
- Write: `frontend/src/App.jsx`
- Write: `frontend/src/App.css`

- [ ] **Step 1: Write `frontend/src/App.jsx`**

```jsx
import { useState } from 'react';
import SyncBar from './components/SyncBar';
import SearchFilters from './components/SearchFilters';
import TradesTable from './components/TradesTable';
import { searchTrades } from './api';
import './App.css';

export default function App() {
  const [trades, setTrades] = useState([]);
  const [lastSymbol, setLastSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSearch({ symbol, expiry, strike }) {
    setLoading(true);
    setError(null);
    setLastSymbol(symbol);
    try {
      const results = await searchTrades({ symbol, expiry, strike });
      setTrades(results);
    } catch (err) {
      setError(err.message);
      setTrades([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Wash Sale Checker</h1>
      </header>
      <SyncBar />
      <main className="app-main">
        <SearchFilters onSearch={handleSearch} />
        {loading && <p className="loading">Searching...</p>}
        {error && <p className="error">{error}</p>}
        {!loading && <TradesTable trades={trades} symbol={lastSymbol} />}
      </main>
    </div>
  );
}
```

- [ ] **Step 2: Write `frontend/src/App.css`**

```css
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui, sans-serif; background: #f5f5f5; color: #222; }

.app { max-width: 1200px; margin: 0 auto; padding: 16px; }
.app-header { padding: 16px 0 8px; }
.app-header h1 { font-size: 1.5rem; font-weight: 700; }
.app-main { display: flex; flex-direction: column; gap: 16px; }

/* Sync Bar */
.sync-bar {
  display: flex; align-items: center; gap: 12px; padding: 12px 16px;
  background: #fff; border-radius: 8px; margin: 12px 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.sync-timestamp { flex: 1; font-size: 0.9rem; color: #555; }
.sync-error { color: #c0392b; font-size: 0.85rem; }
.sync-button {
  padding: 6px 16px; background: #2c3e50; color: #fff;
  border: none; border-radius: 4px; cursor: pointer; font-size: 0.9rem;
}
.sync-button:disabled { opacity: 0.5; cursor: not-allowed; }

/* Search Filters */
.search-filters {
  display: flex; gap: 16px; align-items: flex-end; padding: 16px;
  background: #fff; border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1); flex-wrap: wrap;
}
.filter-group { display: flex; flex-direction: column; gap: 4px; }
.filter-group span { font-size: 0.8rem; color: #666; font-weight: 600; }
.filter-group input {
  padding: 6px 10px; border: 1px solid #ddd;
  border-radius: 4px; font-size: 0.9rem; width: 160px;
}
.search-filters button {
  padding: 7px 20px; background: #27ae60; color: #fff;
  border: none; border-radius: 4px; cursor: pointer; font-size: 0.9rem;
}

/* Trades Table */
.trades-section {
  background: #fff; border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden;
}
.trades-count { padding: 12px 16px; font-size: 0.9rem; color: #555; border-bottom: 1px solid #eee; }
.table-scroll { overflow-x: auto; }
.trades-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.trades-table th {
  background: #f8f8f8; padding: 10px 12px; text-align: left;
  font-weight: 600; border-bottom: 2px solid #e0e0e0; white-space: nowrap;
}
.trades-table td { padding: 8px 12px; border-bottom: 1px solid #f0f0f0; }

/* Row status */
.row-status-open { background: #fff; font-weight: 600; }
.row-status-closed { background: #fafafa; color: #555; }

/* Side */
.side-buy { color: #27ae60; font-weight: 700; }
.side-sell { color: #c0392b; font-weight: 700; }

/* Badges */
.badge {
  display: inline-block; padding: 2px 8px; border-radius: 12px;
  font-size: 0.78rem; font-weight: 600; text-transform: capitalize;
}
.badge-call { background: #dbeafe; color: #1d4ed8; }
.badge-put { background: #ffedd5; color: #c2410c; }
.badge-na { background: #f3f4f6; color: #6b7280; }
.badge-status-open { background: #dcfce7; color: #166534; }
.badge-status-closed { background: #f3f4f6; color: #374151; }
.badge-strategy { background: #f3e8ff; color: #7e22ce; }

/* Empty / utility */
.trades-empty {
  padding: 32px; text-align: center; color: #888;
  background: #fff; border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.loading { padding: 16px; color: #555; }
.error { padding: 16px; color: #c0392b; }
```

- [ ] **Step 3: End-to-end verification in browser**

```bash
# Terminal 1
python -m backend.main

# Terminal 2
cd frontend && npm run dev
```

Open `http://localhost:5173` and verify:
1. Sync bar shows "Never synced" and an active Sync Now button
2. Clicking Sync Now → button shows spinner, status updates
3. Search bar accepts Symbol (required), Expiry and Strike (optional)
4. Searching a symbol with no trades shows "No trades found for X in the last 30 days"
5. After a real sync, searching a traded symbol shows results with all 12 columns
6. Buy rows are green, sell rows are red
7. Open rows are bold/white; closed rows are gray/lighter
8. Call badge is blue, put badge is orange, strategy badge is purple

- [ ] **Step 4: Commit**

```bash
git add frontend/src/App.jsx frontend/src/App.css
git commit -m "feat: App integration — full wash sale checker UI"
```
