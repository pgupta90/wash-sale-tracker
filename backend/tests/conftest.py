import pytest
from unittest.mock import patch


DUMMY_CONFIG = {
    'robinhood': {
        'username': 'test@example.com',
        'password': 'testpassword',
    },
    'schwab': {
        'client_id': 'dummy_client_id',
        'client_secret': 'dummy_client_secret',
    },
}


@pytest.fixture
def mock_config():
    with patch('backend.config.load_config', return_value=DUMMY_CONFIG), \
         patch('backend.routes.auth.load_config', return_value=DUMMY_CONFIG):
        yield DUMMY_CONFIG


@pytest.fixture
def mock_config_no_route_patch():
    """Patches load_config at the config module level only."""
    with patch('backend.config.load_config', return_value=DUMMY_CONFIG):
        yield DUMMY_CONFIG
