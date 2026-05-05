#!/usr/bin/env python3
"""
Run this script ONCE from your terminal to authenticate with Robinhood.
It handles the full MFA flow interactively, then saves a session token.
After this, the backend server will log in automatically on every restart.

Usage:
    python3 backend/authenticate.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import robin_stocks.robinhood as r
from backend.config import load_config

config = load_config()
creds = config.get('robinhood', {})
username = creds.get('username', '')
password = creds.get('password', '')

if not username or username == 'your_email@example.com':
    print("ERROR: Update config.yaml with your real Robinhood credentials first.")
    sys.exit(1)

print(f"Logging in as {username}...")
print()
print("Step 1/2: Approve the login request on your Robinhood app now.")
print("Step 2/2: You will then be prompted for your Google Authenticator code.")
print()

try:
    r.login(username=username, password=password, store_session=True, by_sms=False)
    profile = r.account.load_account_profile()
    print()
    print("Authentication successful!")
    print("Session saved — the backend server will log in automatically from now on.")
    print()
    print("Start the backend: python3 -m backend.main")
except Exception as e:
    print(f"\nAuthentication failed: {e}")
    sys.exit(1)
