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
