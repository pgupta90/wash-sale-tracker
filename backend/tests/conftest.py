import pytest
from unittest.mock import patch


DUMMY_CONFIG = {
    'robinhood': {
        'username': 'test@example.com',
        'password': 'testpassword',
    },
}


@pytest.fixture
def mock_config():
    with patch('backend.config.load_config', return_value=DUMMY_CONFIG), \
         patch('backend.routes.auth.load_config', return_value=DUMMY_CONFIG):
        yield DUMMY_CONFIG
