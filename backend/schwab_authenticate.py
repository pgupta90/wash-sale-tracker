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
