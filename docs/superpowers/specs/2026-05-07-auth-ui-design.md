# Auth UI & Design Refresh — Design Spec

## Goal

Integrate platform authentication into the UI, add stale-sync indicators, and restyle the app with Robinhood's design language.

## Design Language

Matches Robinhood's visual style:
- **Background**: page `#f5f5f5`, cards `#ffffff`
- **Primary green**: `#00c805` — connected state, Sync Now buttons, CTAs
- **Red**: `#ff5000` — disconnected, errors
- **Amber**: `#f5a623` — stale data warning
- **Header tint**: `#f0faf0` (soft sage/mint pastel — light green tint)
- **Borders**: `1px solid #e0e0e0`
- **Typography**: system-ui / Inter, clean and minimal
- **Badges**: pill-shaped, tight padding
- **Cards**: white, subtle shadow, no heavy chrome

---

## Section 1: Header & Auth Status Bar

The app header has two parts:

**Top row** — app title on a pastel sage-green background (`#f0faf0`):
```
Wash Sale Checker
```

**Auth status row** — inline per platform, immediately below title:
```
● Robinhood [Connect]     ● Schwab [Connect]
```

- Green dot (`#00c805`) + "Connected" when token valid
- Red dot (`#ff5000`) + "Not connected" when token missing/expired
- `[Connect]` button appears inline next to the platform name, only when not connected
- Clicking `[Connect Robinhood]` → opens Robinhood modal (see Section 3)
- Clicking `[Connect Schwab]` → calls `GET /auth/schwab/connect`, opens returned URL in browser tab

On app load, both platforms' auth status is fetched from:
- `GET /auth/status` → Robinhood
- `GET /auth/schwab/status` → Schwab

The UI polls these every 5 seconds while a connection is in progress (to pick up when Schwab callback completes).

---

## Section 2: Sync Bar

White card below the header, one row per platform:

```
Robinhood   Last synced: May 4, 2026 ⚠️     [Sync Now]
Schwab      Never synced                    [Sync Now]
```

**Stale indicator:**
- If `last_synced` is older than 24 hours: timestamp turns amber (`#f5a623`) and shows `⚠️`
- "Never synced": muted gray text
- Stale threshold is 24 hours (hardcoded — not configurable)

**Sync Now button:**
- Robinhood green pill, spins while syncing
- Disabled during active sync
- Shows inline error in red if sync fails

---

## Section 3: Robinhood Connect Modal

Triggered by "Connect Robinhood" button. A centered modal overlay:

```
┌─────────────────────────────────────────┐
│  Connect Robinhood                   ✕  │
│                                         │
│  Robinhood uses push notification       │
│  auth that requires your terminal.      │
│                                         │
│  1. Open Terminal                       │
│  2. Run this command:                   │
│  ┌─────────────────────────────────┐    │
│  │ python3 backend/authenticate.py │ □  │
│  └─────────────────────────────────┘    │
│  3. Approve on your Robinhood app       │
│  4. Return here and click Done          │
│                                         │
│                      [Done, Refresh]    │
└─────────────────────────────────────────┘
```

- Code block has a copy-to-clipboard button (`□`)
- "Done, Refresh" button calls `GET /auth/status` and closes the modal if authenticated, otherwise shows "Still not connected — did you complete the steps?"
- Modal has an `✕` close button and closes on backdrop click

---

## Section 4: Schwab OAuth In-Browser Flow

**New backend endpoints:**

`GET /auth/schwab/connect`
- Generates the Schwab authorization URL using `schwab.auth.oauth_client.get_auth_url()`
- Returns `{ "url": "https://api.schwabapi.com/v1/oauth/authorize?..." }`
- Frontend opens this URL in the current browser tab

`GET /auth/schwab/callback`
- FastAPI route that receives `?code=...&state=...` from Schwab after user approves
- Calls schwab-py to exchange the code for tokens and save to `~/.tokens/schwab_token.json`
- On success: redirects browser to `http://localhost:5173?schwab=connected`
- On failure: redirects to `http://localhost:5173?schwab=error&reason=<message>`

**Frontend handling:**
- On mount, App checks URL params for `?schwab=connected` → shows success toast and clears the param
- Polling `GET /auth/schwab/status` every 5 seconds while connection is in progress picks this up automatically

**Schwab developer app update required:**
- Callback URL in developer.schwab.com must be changed to: `http://localhost:8000/auth/schwab/callback`
- `redirect_uri` in `config.yaml` updated to match

---

## Section 5: New & Modified Files

| File | Action | Change |
|---|---|---|
| `frontend/src/components/AuthBar.jsx` | Create | Platform status badges + Connect buttons |
| `frontend/src/components/RobinhoodModal.jsx` | Create | Step-by-step terminal instructions modal |
| `frontend/src/components/SyncBar.jsx` | Modify | Stale indicator, Robinhood green buttons |
| `frontend/src/App.jsx` | Modify | Add AuthBar, handle `?schwab=connected` param |
| `frontend/src/App.css` | Modify | Full Robinhood design language restyle |
| `frontend/src/api.js` | Modify | Add `getSchwabConnectUrl()` |
| `backend/routes/auth.py` | Modify | Add `GET /auth/schwab/connect`, `GET /auth/schwab/callback` |
| `config.yaml` + `config.yaml.example` | Modify | Update `redirect_uri` to `http://localhost:8000/auth/schwab/callback` |

---

## Error States

| State | Display |
|---|---|
| Schwab token expired | Red dot "Expired — reconnect" + Connect button |
| Schwab callback error | Toast: "Schwab connection failed: `<reason>`" |
| Robinhood not authenticated | Red dot + Connect button |
| Sync fails | Inline red text in sync row |
| Stale data | Amber timestamp + ⚠️ |
