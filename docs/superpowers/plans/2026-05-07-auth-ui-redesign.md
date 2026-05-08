# Auth UI & Design Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add per-platform auth status to the header, Schwab in-browser OAuth2 callback flow, stale sync indicators, and restyle the entire app with Robinhood's design language.

**Architecture:** Two new FastAPI endpoints handle Schwab OAuth (`/auth/schwab/connect` returns the URL, `/auth/schwab/callback` exchanges the code and redirects). The frontend adds an `AuthBar` component (inline status + Connect buttons), a `RobinhoodModal` (terminal command instructions), and a full CSS restyle. App.jsx adds URL param handling for the Schwab redirect.

**Tech Stack:** FastAPI + httpx (backend OAuth token exchange), React + Vite (frontend)

---

## File Map

| File | Action |
|---|---|
| `backend/routes/auth.py` | Add `GET /auth/schwab/connect` and `GET /auth/schwab/callback` |
| `backend/tests/test_routes_auth.py` | Add tests for two new endpoints |
| `config.yaml.example` | Update `redirect_uri` to `http://localhost:8000/auth/schwab/callback` |
| `frontend/src/api.js` | Add `getSchwabAuthStatus()`, `getSchwabConnectUrl()` |
| `frontend/src/components/AuthBar.jsx` | Create: per-platform status dots + Connect buttons |
| `frontend/src/components/RobinhoodModal.jsx` | Create: terminal instruction modal |
| `frontend/src/components/SyncBar.jsx` | Modify: stale indicator (amber/⚠️), white card, green button |
| `frontend/src/App.jsx` | Modify: add AuthBar, pastel header, `?schwab=connected` toast |
| `frontend/src/App.css` | Modify: full Robinhood design language restyle |

---

### Task 1: Backend — Schwab OAuth Endpoints

**Files:**
- Modify: `backend/routes/auth.py`
- Modify: `backend/tests/test_routes_auth.py`

- [ ] **Step 1: Write the failing tests**

Add to `backend/tests/test_routes_auth.py`:

```python
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app, follow_redirects=False)

def test_schwab_connect_returns_url(mock_config):
    # mock_config fixture already patches load_config with schwab creds
    resp = client.get('/auth/schwab/connect')
    assert resp.status_code == 200
    data = resp.json()
    assert 'url' in data
    assert 'api.schwabapi.com' in data['url']
    assert 'response_type=code' in data['url']

def test_schwab_callback_success_redirects(mock_config):
    mock_token = {
        'access_token': 'tok_abc',
        'refresh_token': 'ref_abc',
        'token_type': 'Bearer',
        'expires_in': 1800,
    }
    with patch('backend.routes.auth.httpx.post') as mock_post, \
         patch('backend.routes.auth.open', create=True), \
         patch('backend.routes.auth.os.makedirs'):
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_token
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        resp = client.get('/auth/schwab/callback?code=abc123')

    assert resp.status_code in (302, 307)
    assert 'schwab=connected' in resp.headers['location']

def test_schwab_callback_failure_redirects_with_error(mock_config):
    with patch('backend.routes.auth.httpx.post') as mock_post, \
         patch('backend.routes.auth.os.makedirs'):
        mock_post.side_effect = Exception('token exchange failed')
        resp = client.get('/auth/schwab/callback?code=bad')

    assert resp.status_code in (302, 307)
    assert 'schwab=error' in resp.headers['location']
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/priya/Documents/claude-projects/WashSaleApp
python -m pytest backend/tests/test_routes_auth.py::test_schwab_connect_returns_url backend/tests/test_routes_auth.py::test_schwab_callback_success_redirects backend/tests/test_routes_auth.py::test_schwab_callback_failure_redirects_with_error -v
```

Expected: FAIL (endpoints don't exist yet)

- [ ] **Step 3: Implement the endpoints**

Replace `backend/routes/auth.py` with:

```python
import os
import json
import time
import base64
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from backend.auth import get_auth_status
from backend.schwab_auth import get_schwab_status
from backend.config import load_config
from backend.models import AuthStatus

router = APIRouter(prefix='/auth', tags=['auth'])

TOKEN_PATH = os.path.expanduser('~/.tokens/schwab_token.json')
FRONTEND_URL = 'http://localhost:5173'
CALLBACK_URI = 'http://localhost:8000/auth/schwab/callback'


@router.get('/status', response_model=AuthStatus)
def auth_status():
    return get_auth_status()


@router.get('/schwab/status', response_model=AuthStatus)
def schwab_auth_status():
    return get_schwab_status()


@router.get('/schwab/connect')
def schwab_connect():
    config = load_config()
    client_id = config.get('schwab', {}).get('client_id', '')
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': CALLBACK_URI,
    }
    url = f"https://api.schwabapi.com/v1/oauth/authorize?{urlencode(params)}"
    return {'url': url}


@router.get('/schwab/callback')
def schwab_callback(code: str, session: str = None):
    config = load_config()
    creds = config.get('schwab', {})
    client_id = creds.get('client_id', '')
    client_secret = creds.get('client_secret', '')

    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    try:
        resp = httpx.post(
            'https://api.schwabapi.com/v1/oauth/token',
            headers={
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': CALLBACK_URI,
            },
        )
        resp.raise_for_status()
        token_data = resp.json()
    except Exception as e:
        safe = str(e).replace(' ', '+')
        return RedirectResponse(f'{FRONTEND_URL}?schwab=error&reason={safe}')

    token_data['expires_at'] = time.time() + token_data.get('expires_in', 1800)

    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
    with open(TOKEN_PATH, 'w') as f:
        json.dump(token_data, f)

    return RedirectResponse(f'{FRONTEND_URL}?schwab=connected')
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest backend/tests/test_routes_auth.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add backend/routes/auth.py backend/tests/test_routes_auth.py
git commit -m "feat: add Schwab OAuth connect and callback endpoints"
```

---

### Task 2: Update Config Example

**Files:**
- Modify: `config.yaml.example`

> **Note for user:** After this task, also update your personal `config.yaml` — change `schwab.redirect_uri` to `http://localhost:8000/auth/schwab/callback` and register this URL in your Schwab developer app at developer.schwab.com.

- [ ] **Step 1: Update `config.yaml.example`**

Find the `schwab:` section in `config.yaml.example`. Change the `redirect_uri` line from `https://127.0.0.1` (or whatever it currently is) to:

```yaml
schwab:
  client_id: your_schwab_app_key_here
  client_secret: your_schwab_secret_here
  redirect_uri: http://localhost:8000/auth/schwab/callback
```

- [ ] **Step 2: Commit**

```bash
git add config.yaml.example
git commit -m "config: update Schwab redirect_uri to FastAPI callback"
```

---

### Task 3: Frontend API Client Additions

**Files:**
- Modify: `frontend/src/api.js`

- [ ] **Step 1: Add two new functions to `frontend/src/api.js`**

Add after the existing `getAuthStatus` function:

```javascript
export async function getSchwabAuthStatus() {
  const res = await fetch(`${BASE}/auth/schwab/status`);
  if (!res.ok) throw new Error('Failed to fetch Schwab auth status');
  return res.json();
}

export async function getSchwabConnectUrl() {
  const res = await fetch(`${BASE}/auth/schwab/connect`);
  if (!res.ok) throw new Error('Failed to get Schwab connect URL');
  return res.json();
}
```

- [ ] **Step 2: Verify the dev server still starts without errors**

```bash
cd /Users/priya/Documents/claude-projects/WashSaleApp/frontend && npm run build 2>&1 | tail -5
```

Expected: no errors (build succeeds or only expected warnings)

- [ ] **Step 3: Commit**

```bash
git add frontend/src/api.js
git commit -m "feat: add getSchwabAuthStatus and getSchwabConnectUrl to api client"
```

---

### Task 4: Create AuthBar Component

**Files:**
- Create: `frontend/src/components/AuthBar.jsx`

The AuthBar shows one row per platform: a colored dot, platform name, connected/disconnected text, and a [Connect] button when not authenticated. It polls auth status every 5 seconds while `polling` is true (set after a connect attempt is initiated).

- [ ] **Step 1: Create `frontend/src/components/AuthBar.jsx`**

```jsx
import { useState, useEffect, useRef } from 'react';
import { getAuthStatus, getSchwabAuthStatus, getSchwabConnectUrl } from '../api';

function PlatformAuthRow({ name, getStatus, onConnectClick, isConnecting }) {
  const [status, setStatus] = useState({ authenticated: false });

  const refresh = () => getStatus().then(setStatus).catch(console.error);

  useEffect(() => {
    refresh();
  }, []);

  useEffect(() => {
    if (!isConnecting) return;
    const id = setInterval(refresh, 5000);
    return () => clearInterval(id);
  }, [isConnecting]);

  return (
    <div className="auth-bar-row">
      <span className={`auth-dot ${status.authenticated ? 'auth-dot-connected' : 'auth-dot-disconnected'}`} />
      <span className="auth-platform-name">{name}</span>
      <span className={`auth-status-text ${status.authenticated ? 'auth-connected' : 'auth-disconnected'}`}>
        {status.authenticated ? 'Connected' : 'Not connected'}
      </span>
      {!status.authenticated && (
        <button className="auth-connect-btn" onClick={onConnectClick}>
          Connect
        </button>
      )}
    </div>
  );
}

export default function AuthBar({ onConnectRobinhood, schwabConnecting }) {
  async function handleConnectSchwab() {
    try {
      const { url } = await getSchwabConnectUrl();
      window.open(url, '_blank');
    } catch (err) {
      console.error('Failed to get Schwab connect URL', err);
    }
  }

  return (
    <div className="auth-bar">
      <PlatformAuthRow
        name="Robinhood"
        getStatus={getAuthStatus}
        onConnectClick={onConnectRobinhood}
        isConnecting={false}
      />
      <PlatformAuthRow
        name="Schwab"
        getStatus={getSchwabAuthStatus}
        onConnectClick={handleConnectSchwab}
        isConnecting={schwabConnecting}
      />
    </div>
  );
}
```

- [ ] **Step 2: Verify build passes**

```bash
cd /Users/priya/Documents/claude-projects/WashSaleApp/frontend && npm run build 2>&1 | tail -5
```

Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/AuthBar.jsx
git commit -m "feat: add AuthBar component with per-platform connect buttons"
```

---

### Task 5: Create RobinhoodModal Component

**Files:**
- Create: `frontend/src/components/RobinhoodModal.jsx`

The modal shows step-by-step terminal instructions with a copy button. "Done, Refresh" calls `GET /auth/status` and closes if authenticated, otherwise shows an error message.

- [ ] **Step 1: Create `frontend/src/components/RobinhoodModal.jsx`**

```jsx
import { useState } from 'react';
import { getAuthStatus } from '../api';

const COMMAND = 'python3 backend/authenticate.py';

export default function RobinhoodModal({ onClose }) {
  const [copyLabel, setCopyLabel] = useState('Copy');
  const [checking, setChecking] = useState(false);
  const [notConnected, setNotConnected] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(COMMAND).then(() => {
      setCopyLabel('Copied!');
      setTimeout(() => setCopyLabel('Copy'), 2000);
    });
  }

  async function handleDone() {
    setChecking(true);
    setNotConnected(false);
    try {
      const status = await getAuthStatus();
      if (status.authenticated) {
        onClose();
      } else {
        setNotConnected(true);
      }
    } catch {
      setNotConnected(true);
    } finally {
      setChecking(false);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">Connect Robinhood</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          <p className="modal-instruction">
            Robinhood uses push notification auth that requires your terminal.
          </p>
          <ol className="modal-steps">
            <li>Open Terminal</li>
            <li>
              Run this command:
              <div className="modal-command-block">
                <code>{COMMAND}</code>
                <button className="modal-copy-btn" onClick={handleCopy}>{copyLabel}</button>
              </div>
            </li>
            <li>Approve on your Robinhood app</li>
            <li>Return here and click Done</li>
          </ol>
          {notConnected && (
            <p className="modal-error">
              Still not connected — did you complete the steps?
            </p>
          )}
        </div>
        <div className="modal-footer">
          <button className="modal-done-btn" onClick={handleDone} disabled={checking}>
            {checking ? 'Checking...' : 'Done, Refresh'}
          </button>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify build passes**

```bash
cd /Users/priya/Documents/claude-projects/WashSaleApp/frontend && npm run build 2>&1 | tail -5
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/RobinhoodModal.jsx
git commit -m "feat: add RobinhoodModal with terminal instructions and copy button"
```

---

### Task 6: Update SyncBar — Stale Indicator & Styles

**Files:**
- Modify: `frontend/src/components/SyncBar.jsx`

Changes:
- Add stale detection (>24 hours → amber timestamp + ⚠️)
- Add `sync-timestamp-stale` class when stale
- Change button class from `sync-button` to `sync-button-green` (CSS will be updated in Task 8)

- [ ] **Step 1: Update `frontend/src/components/SyncBar.jsx`**

```jsx
import { useState, useEffect } from 'react';
import {
  getSyncStatus, triggerSync,
  getSchwabSyncStatus, triggerSchwabSync,
} from '../api';

const STALE_MS = 24 * 60 * 60 * 1000;

function isStale(lastSynced) {
  if (!lastSynced) return false;
  return Date.now() - new Date(lastSynced).getTime() > STALE_MS;
}

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

  const stale = isStale(syncState.last_synced);

  let timestampText;
  if (syncState.status === 'syncing') {
    timestampText = 'Syncing...';
  } else if (syncState.last_synced) {
    timestampText = `Last synced: ${new Date(syncState.last_synced).toLocaleString()}`;
  } else {
    timestampText = 'Never synced';
  }

  return (
    <div className="sync-bar-row">
      <span className="sync-platform">{name}</span>
      <span className={`sync-timestamp${stale ? ' sync-timestamp-stale' : ''}`}>
        {timestampText}{stale ? ' ⚠️' : ''}
      </span>
      {syncState.status === 'error' && (
        <span className="sync-error"> — {syncState.error}</span>
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

- [ ] **Step 2: Verify build passes**

```bash
cd /Users/priya/Documents/claude-projects/WashSaleApp/frontend && npm run build 2>&1 | tail -5
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/SyncBar.jsx
git commit -m "feat: add 24h stale indicator to SyncBar"
```

---

### Task 7: Update App.jsx — AuthBar, Schwab Param, Toast

**Files:**
- Modify: `frontend/src/App.jsx`

Changes:
- Import `AuthBar` and `RobinhoodModal`
- Add `showRobinhoodModal` state
- Add `schwabConnecting` state (true after Connect Schwab clicked, until status confirmed)
- On mount: check `?schwab=connected` URL param → show toast, clear param
- Add toast state for success/error messages

- [ ] **Step 1: Update `frontend/src/App.jsx`**

```jsx
import { useState, useEffect } from 'react';
import AuthBar from './components/AuthBar';
import RobinhoodModal from './components/RobinhoodModal';
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
  const [showRobinhoodModal, setShowRobinhoodModal] = useState(false);
  const [schwabConnecting, setSchwabConnecting] = useState(false);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('schwab') === 'connected') {
      setToast({ type: 'success', message: 'Schwab connected successfully!' });
      setSchwabConnecting(false);
      params.delete('schwab');
      const newUrl = window.location.pathname + (params.toString() ? `?${params}` : '');
      window.history.replaceState({}, '', newUrl);
    } else if (params.get('schwab') === 'error') {
      const reason = params.get('reason') || 'Unknown error';
      setToast({ type: 'error', message: `Schwab connection failed: ${reason}` });
      params.delete('schwab');
      params.delete('reason');
      const newUrl = window.location.pathname + (params.toString() ? `?${params}` : '');
      window.history.replaceState({}, '', newUrl);
    }
  }, []);

  useEffect(() => {
    if (!toast) return;
    const id = setTimeout(() => setToast(null), 5000);
    return () => clearTimeout(id);
  }, [toast]);

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
        <div className="app-header-title-row">
          <h1>Wash Sale Checker</h1>
        </div>
        <AuthBar
          onConnectRobinhood={() => setShowRobinhoodModal(true)}
          schwabConnecting={schwabConnecting}
          onSchwabConnectInitiated={() => setSchwabConnecting(true)}
        />
      </header>

      {toast && (
        <div className={`toast toast-${toast.type}`}>{toast.message}</div>
      )}

      <SyncBar />

      <main className="app-main">
        <SearchFilters onSearch={handleSearch} />
        {loading && <p className="loading">Searching...</p>}
        {error && <p className="error">{error}</p>}
        {!loading && <TradesTable trades={trades} symbol={lastSymbol} />}
      </main>

      {showRobinhoodModal && (
        <RobinhoodModal onClose={() => setShowRobinhoodModal(false)} />
      )}
    </div>
  );
}
```

Also update `AuthBar.jsx` to call `onSchwabConnectInitiated` before opening the Schwab URL — replace `handleConnectSchwab` in `AuthBar.jsx`:

```jsx
// In AuthBar.jsx, update the component signature and handleConnectSchwab:
export default function AuthBar({ onConnectRobinhood, schwabConnecting, onSchwabConnectInitiated }) {
  async function handleConnectSchwab() {
    try {
      const { url } = await getSchwabConnectUrl();
      if (onSchwabConnectInitiated) onSchwabConnectInitiated();
      window.open(url, '_blank');
    } catch (err) {
      console.error('Failed to get Schwab connect URL', err);
    }
  }
  // ... rest unchanged
```

- [ ] **Step 2: Verify build passes**

```bash
cd /Users/priya/Documents/claude-projects/WashSaleApp/frontend && npm run build 2>&1 | tail -5
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/App.jsx frontend/src/components/AuthBar.jsx
git commit -m "feat: wire up AuthBar, RobinhoodModal, and Schwab connect param handling in App"
```

---

### Task 8: Full CSS Restyle — Robinhood Design Language

**Files:**
- Modify: `frontend/src/App.css`

Complete restyle: pastel sage header, white cards, Robinhood green CTAs, amber stale, per-platform auth bar, modal styles.

- [ ] **Step 1: Replace `frontend/src/App.css` with the full Robinhood design**

```css
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui, -apple-system, 'Inter', sans-serif; background: #f5f5f5; color: #222; }

/* ── Layout ── */
.app { max-width: 1200px; margin: 0 auto; }
.app-main { display: flex; flex-direction: column; gap: 16px; padding: 16px; }

/* ── Header ── */
.app-header {
  background: #f0faf0;
  border-bottom: 1px solid #d4ecd4;
}

.app-header-title-row {
  padding: 14px 20px 8px;
}

.app-header h1 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111;
  letter-spacing: -0.01em;
}

/* ── Auth Bar ── */
.auth-bar {
  display: flex;
  gap: 0;
  padding: 0 20px 12px;
  flex-wrap: wrap;
  gap: 0 32px;
}

.auth-bar-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
}

.auth-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.auth-dot-connected { background: #00c805; }
.auth-dot-disconnected { background: #ff5000; }

.auth-platform-name {
  font-weight: 600;
  color: #333;
}

.auth-status-text { color: #666; }
.auth-connected { color: #00c805; }
.auth-disconnected { color: #ff5000; }

.auth-connect-btn {
  background: none;
  border: 1px solid #00c805;
  color: #00c805;
  border-radius: 12px;
  padding: 2px 10px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.auth-connect-btn:hover {
  background: #e8fde8;
}

/* ── Sync Bar ── */
.sync-bar {
  background: #ffffff;
  border-bottom: 1px solid #e0e0e0;
  border-top: none;
  padding: 0;
}

.sync-bar-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.sync-bar-row:last-child { border-bottom: none; }

.sync-platform {
  font-weight: 600;
  color: #333;
  font-size: 0.85rem;
  width: 80px;
  flex-shrink: 0;
}

.sync-timestamp {
  color: #777;
  font-size: 0.85rem;
  flex: 1;
}

.sync-timestamp-stale {
  color: #f5a623;
  font-weight: 600;
}

.sync-error {
  color: #ff5000;
  font-size: 0.82rem;
}

.sync-button {
  background: #00c805;
  color: white;
  border: none;
  padding: 5px 14px;
  border-radius: 16px;
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 600;
  flex-shrink: 0;
  transition: background 0.15s;
}

.sync-button:hover:not(:disabled) { background: #00b004; }

.sync-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Toast ── */
.toast {
  margin: 12px 16px 0;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 0.88rem;
  font-weight: 500;
}

.toast-success { background: #e8fde8; color: #166534; border: 1px solid #86efac; }
.toast-error { background: #fff0eb; color: #c2410c; border: 1px solid #fdba74; }

/* ── Search Filters ── */
.search-filters {
  display: flex; gap: 16px; align-items: flex-end; padding: 16px;
  background: #fff; border-radius: 8px;
  border: 1px solid #e0e0e0;
  flex-wrap: wrap;
}

.filter-group { display: flex; flex-direction: column; gap: 4px; }
.filter-group span { font-size: 0.78rem; color: #666; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.filter-group input {
  padding: 7px 10px; border: 1px solid #ddd;
  border-radius: 6px; font-size: 0.9rem; width: 160px;
  outline: none;
}
.filter-group input:focus { border-color: #00c805; }

.search-filters button {
  padding: 8px 22px; background: #00c805; color: #fff;
  border: none; border-radius: 16px; cursor: pointer; font-size: 0.88rem;
  font-weight: 700; transition: background 0.15s;
}
.search-filters button:hover { background: #00b004; }

/* ── Trades Table ── */
.trades-section {
  background: #fff; border-radius: 8px;
  border: 1px solid #e0e0e0; overflow: hidden;
}
.trades-count { padding: 12px 16px; font-size: 0.88rem; color: #555; border-bottom: 1px solid #eee; }
.table-scroll { overflow-x: auto; }
.trades-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.trades-table th {
  background: #f8f8f8; padding: 10px 12px; text-align: left;
  font-weight: 600; border-bottom: 2px solid #e0e0e0; white-space: nowrap;
  font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.03em; color: #666;
}
.trades-table td { padding: 9px 12px; border-bottom: 1px solid #f0f0f0; }

/* Row status */
.row-status-open { background: #fff; }
.row-status-closed { background: #fafafa; color: #666; }

/* Side */
.side-buy { color: #00c805; font-weight: 700; }
.side-sell { color: #ff5000; font-weight: 700; }

/* Badges */
.badge {
  display: inline-block; padding: 2px 8px; border-radius: 12px;
  font-size: 0.75rem; font-weight: 600; text-transform: capitalize;
}
.badge-call { background: #dbeafe; color: #1d4ed8; }
.badge-put { background: #ffedd5; color: #c2410c; }
.badge-na { background: #f3f4f6; color: #6b7280; }
.badge-status-open { background: #e8fde8; color: #166534; }
.badge-status-closed { background: #f3f4f6; color: #374151; }
.badge-strategy { background: #f3e8ff; color: #7e22ce; }

/* Empty / utility */
.trades-empty {
  padding: 40px; text-align: center; color: #999;
  background: #fff; border-radius: 8px; border: 1px solid #e0e0e0;
}
.loading { padding: 16px; color: #555; }
.error { padding: 16px; color: #ff5000; }

/* ── Modal ── */
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: #fff;
  border-radius: 12px;
  width: 420px;
  max-width: calc(100vw - 32px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  overflow: hidden;
}

.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px 12px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-title {
  font-weight: 700;
  font-size: 1rem;
  color: #111;
}

.modal-close {
  background: none; border: none; cursor: pointer;
  color: #888; font-size: 1rem; padding: 2px 4px;
  line-height: 1;
}
.modal-close:hover { color: #333; }

.modal-body { padding: 16px 20px; }

.modal-instruction {
  font-size: 0.88rem; color: #555; margin-bottom: 14px; line-height: 1.5;
}

.modal-steps {
  font-size: 0.88rem; color: #333;
  padding-left: 20px;
  display: flex; flex-direction: column; gap: 8px;
  line-height: 1.6;
}

.modal-command-block {
  display: flex; align-items: center; gap: 8px;
  background: #f5f5f5; border: 1px solid #e0e0e0;
  border-radius: 6px; padding: 7px 10px; margin-top: 6px;
}

.modal-command-block code {
  font-family: 'SF Mono', 'Fira Mono', monospace;
  font-size: 0.82rem; color: #222; flex: 1;
}

.modal-copy-btn {
  background: none; border: 1px solid #ccc; border-radius: 4px;
  padding: 2px 8px; font-size: 0.75rem; cursor: pointer; color: #555;
  flex-shrink: 0;
}
.modal-copy-btn:hover { background: #efefef; }

.modal-error {
  margin-top: 12px; font-size: 0.82rem;
  color: #ff5000; background: #fff0eb;
  border: 1px solid #fdba74; border-radius: 6px;
  padding: 8px 12px;
}

.modal-footer {
  padding: 12px 20px 16px;
  display: flex; justify-content: flex-end;
  border-top: 1px solid #f0f0f0;
}

.modal-done-btn {
  background: #00c805; color: white; border: none;
  border-radius: 16px; padding: 8px 22px;
  font-size: 0.88rem; font-weight: 700; cursor: pointer;
  transition: background 0.15s;
}
.modal-done-btn:hover:not(:disabled) { background: #00b004; }
.modal-done-btn:disabled { opacity: 0.5; cursor: not-allowed; }
```

- [ ] **Step 2: Verify build passes**

```bash
cd /Users/priya/Documents/claude-projects/WashSaleApp/frontend && npm run build 2>&1 | tail -5
```

- [ ] **Step 3: Start dev server and visually verify**

Start backend and frontend:
```bash
# In one terminal:
python3 -m backend.main &

# In another:
cd frontend && npm run dev
```

Open `http://localhost:5173` and verify:
- Header: pastel sage-green (#f0faf0) background
- Auth bar: colored dots (red=not connected), Connect buttons with green border
- Sync bar: white background, green Sync Now buttons
- Search button: Robinhood green (#00c805)
- Table: clean white card, uppercase column headers
- Side badges: green buy, red/orange sell

- [ ] **Step 4: Commit**

```bash
git add frontend/src/App.css
git commit -m "feat: full Robinhood design language restyle"
```

---

## Verification

After all tasks complete:

1. Start both servers: `python3 -m backend.main` and `cd frontend && npm run dev`
2. Open `http://localhost:5173`
3. Header shows auth status with colored dots and Connect buttons
4. Click "Connect Robinhood" → modal appears with terminal command and copy button
5. Click "Connect Schwab" → opens Schwab OAuth URL in new tab (if Schwab credentials configured)
6. Sync bar shows white card with green Sync Now buttons
7. If `last_synced` is more than 24 hours ago, timestamp shows in amber with ⚠️
8. After Schwab OAuth completes, browser redirects to `http://localhost:5173?schwab=connected` → green toast appears
9. Run backend tests: `python3 -m pytest backend/tests/ -v` — all pass

**User must also:**
- Update `config.yaml`: change `schwab.redirect_uri` to `http://localhost:8000/auth/schwab/callback`  
- Update Schwab developer app at developer.schwab.com: set callback URL to `http://localhost:8000/auth/schwab/callback`
