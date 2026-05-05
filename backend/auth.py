import robin_stocks.robinhood as r
from backend.config import load_config


def login(username: str, password: str) -> dict:
    """Login to Robinhood. robin_stocks prompts for MFA on the CLI automatically."""
    try:
        r.login(username=username, password=password, store_session=True, by_sms=False)
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
    except Exception as e:
        return {'authenticated': False, 'error': str(e)}
