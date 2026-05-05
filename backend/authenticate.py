#!/usr/bin/env python3
"""
Run this script ONCE from your terminal to authenticate with Robinhood.
Handles: push notification approval on the Robinhood app + Google Authenticator TOTP.
After this, the backend server logs in automatically on every restart.

Usage:
    python3 backend/authenticate.py
"""
import sys
import os
import uuid
import pickle

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import robin_stocks.robinhood as r
from backend.config import load_config

# Robinhood public OAuth client ID (same one robin_stocks uses internally)
CLIENT_ID = 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS'
TOKEN_URL = 'https://api.robinhood.com/oauth2/token/'
DEVICE_TOKEN_FILE = os.path.expanduser('~/.tokens/robinhood_device_token')
PICKLE_FILE = os.path.expanduser('~/.tokens/robinhood.pickle')


def get_device_token():
    """Return a persistent device token so Robinhood recognises this machine."""
    os.makedirs(os.path.dirname(DEVICE_TOKEN_FILE), exist_ok=True)
    if os.path.exists(DEVICE_TOKEN_FILE):
        with open(DEVICE_TOKEN_FILE) as f:
            return f.read().strip()
    token = str(uuid.uuid4())
    with open(DEVICE_TOKEN_FILE, 'w') as f:
        f.write(token)
    return token


def save_session(token_data: dict):
    """Save tokens in the format robin_stocks expects when loading from pickle."""
    os.makedirs(os.path.expanduser('~/.tokens'), exist_ok=True)
    session = {
        'token_type': token_data.get('token_type', 'Bearer'),
        'access_token': token_data['access_token'],
        'refresh_token': token_data.get('refresh_token', ''),
        'expires_in': token_data.get('expires_in', 86400),
        'scope': token_data.get('scope', 'internal'),
        'detail': 'logged in using pickle',
        'backup_code': None,
    }
    with open(PICKLE_FILE, 'wb') as f:
        pickle.dump(session, f)


def setup_robin_stocks_session(access_token: str, token_type: str = 'Bearer'):
    """Wire the token into robin_stocks' live session so we can verify it immediately."""
    r.helper.SESSION.headers.update({
        'Authorization': f'{token_type} {access_token}'
    })


def main():
    config = load_config()
    creds = config.get('robinhood', {})
    username = creds.get('username', '')
    password = creds.get('password', '')

    if not username or username == 'your_email@example.com':
        print("ERROR: Update config.yaml with your real Robinhood credentials first.")
        sys.exit(1)

    device_token = get_device_token()

    base_payload = {
        'client_id': CLIENT_ID,
        'expires_in': 86400,
        'grant_type': 'password',
        'password': password,
        'scope': 'internal',
        'username': username,
        'device_token': device_token,
        'challenge_type': 'email',  # Robinhood overrides this with push notification
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
    }

    print(f"Logging in as {username}...")
    print()

    # ── Step 1: Initial request ──────────────────────────────────────────────
    res = requests.post(TOKEN_URL, data=base_payload, headers=headers)
    data = res.json()

    # ── Step 2: Push notification challenge ──────────────────────────────────
    # Robinhood sends a push notification to the Robinhood app.
    # We MUST wait for the user to approve before retrying — robin_stocks does
    # not wait, which is why r.login() fails before approval.
    if 'challenge' in data:
        challenge_id = data['challenge']['id']
        print("Robinhood has sent a login approval notification to your Robinhood app.")
        print()
        input("→  Approve it on your phone, then press Enter here to continue...")
        print()

        headers['X-ROBINHOOD-CHALLENGE-RESPONSE-ID'] = challenge_id
        res = requests.post(TOKEN_URL, data=base_payload, headers=headers)
        data = res.json()

    # ── Step 3: Google Authenticator TOTP ────────────────────────────────────
    if data.get('mfa_required'):
        mfa_code = input("Enter your 6-digit Google Authenticator code: ").strip()
        totp_payload = dict(base_payload)
        totp_payload['mfa_code'] = mfa_code
        res = requests.post(TOKEN_URL, data=totp_payload, headers=headers)
        data = res.json()

    # ── Check result ─────────────────────────────────────────────────────────
    if 'access_token' not in data:
        print()
        print(f"Authentication failed: {data.get('detail', data)}")
        sys.exit(1)

    # ── Save session + verify ─────────────────────────────────────────────────
    save_session(data)
    setup_robin_stocks_session(data['access_token'], data.get('token_type', 'Bearer'))

    try:
        r.account.load_account_profile()
        print()
        print("Authentication successful! Session saved to ~/.tokens/robinhood.pickle")
        print("The backend will now log in automatically on every restart.")
        print()
        print("Start the backend:  python3 -m backend.main")
    except Exception as e:
        print(f"\nWarning: Authenticated but profile fetch failed: {e}")
        print("Try starting the backend anyway — the session is saved.")


if __name__ == '__main__':
    main()
