import os
import json
import time
import base64
import secrets
from urllib.parse import urlencode, quote_plus, urlparse, parse_qs

import httpx
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from backend.auth import get_auth_status
from backend.schwab_auth import get_schwab_status
from backend.config import load_config
from backend.models import AuthStatus

router = APIRouter(prefix='/auth', tags=['auth'])

TOKEN_PATH = os.path.expanduser('~/.tokens/schwab_token.json')

_pending_states: set = set()


@router.get('/status', response_model=AuthStatus)
def auth_status():
    return get_auth_status()


@router.get('/schwab/status', response_model=AuthStatus)
def schwab_auth_status():
    return get_schwab_status()


@router.get('/schwab/connect')
def schwab_connect():
    config = load_config()
    creds = config.get('schwab', {})
    client_id = creds.get('client_id', '')
    callback_uri = creds.get('redirect_uri', 'http://localhost:8000/auth/schwab/callback')
    frontend_url = config.get('settings', {}).get('frontend_url', 'http://localhost:5173')  # noqa: F841

    state = secrets.token_urlsafe(32)
    _pending_states.add(state)

    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': callback_uri,
        'state': state,
    }
    url = f"https://api.schwabapi.com/v1/oauth/authorize?{urlencode(params)}"
    return {'url': url}


@router.get('/schwab/callback')
def schwab_callback(code: str, state: str = None):
    config = load_config()
    creds = config.get('schwab', {})
    client_id = creds.get('client_id', '')
    client_secret = creds.get('client_secret', '')
    callback_uri = creds.get('redirect_uri', 'http://localhost:8000/auth/schwab/callback')
    frontend_url = config.get('settings', {}).get('frontend_url', 'http://localhost:5173')

    if not state or state not in _pending_states:
        return RedirectResponse(
            f'{frontend_url}?schwab=error&reason={quote_plus("Invalid or missing state parameter")}',
            status_code=302,
        )
    _pending_states.discard(state)

    try:
        token_data = _exchange_schwab_code(
            code=code,
            callback_uri=callback_uri,
            client_id=client_id,
            client_secret=client_secret,
        )
    except Exception as e:
        safe = quote_plus(str(e)[:200])
        return RedirectResponse(f'{frontend_url}?schwab=error&reason={safe}', status_code=302)

    _save_token(token_data)
    return RedirectResponse(f'{frontend_url}?schwab=connected', status_code=302)


class ManualCallbackRequest(BaseModel):
    url: str


def _exchange_schwab_code(code: str, callback_uri: str, client_id: str, client_secret: str) -> dict:
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    resp = httpx.post(
        'https://api.schwabapi.com/v1/oauth/token',
        headers={
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': callback_uri,
        },
    )
    resp.raise_for_status()
    return resp.json()


def _save_token(token_data: dict):
    token_data['expires_at'] = time.time() + token_data.get('expires_in', 1800)
    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
    tmp = TOKEN_PATH + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(token_data, f)
    os.replace(tmp, TOKEN_PATH)


@router.post('/schwab/manual-callback')
def schwab_manual_callback(body: ManualCallbackRequest):
    parsed = urlparse(body.url)
    params = parse_qs(parsed.query)

    code = params.get('code', [None])[0]
    state = params.get('state', [None])[0]

    if not code:
        return {'success': False, 'error': 'No authorization code found in URL'}

    if not state or state not in _pending_states:
        return {'success': False, 'error': 'Invalid or missing state parameter'}
    _pending_states.discard(state)

    config = load_config()
    creds = config.get('schwab', {})
    callback_uri = creds.get('redirect_uri', 'https://127.0.0.1')

    try:
        token_data = _exchange_schwab_code(
            code=code,
            callback_uri=callback_uri,
            client_id=creds.get('client_id', ''),
            client_secret=creds.get('client_secret', ''),
        )
    except Exception as e:
        return {'success': False, 'error': str(e)[:200]}

    _save_token(token_data)
    return {'success': True}
