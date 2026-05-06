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
