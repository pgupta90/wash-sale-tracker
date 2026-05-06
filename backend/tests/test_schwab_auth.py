from unittest.mock import patch, MagicMock
from backend.schwab_auth import get_schwab_status

def test_get_schwab_status_authenticated():
    with patch('backend.schwab_auth.schwab.auth.client_from_token_file') as mock_load:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_client.get_account_numbers.return_value = mock_response
        mock_load.return_value = mock_client
        status = get_schwab_status()
    assert status['authenticated'] is True

def test_get_schwab_status_missing_token():
    with patch('backend.schwab_auth.schwab.auth.client_from_token_file') as mock_load:
        mock_load.side_effect = FileNotFoundError('token not found')
        status = get_schwab_status()
    assert status['authenticated'] is False
    assert 'error' in status

def test_get_schwab_status_expired_token():
    with patch('backend.schwab_auth.schwab.auth.client_from_token_file') as mock_load:
        mock_load.side_effect = Exception('401 Unauthorized')
        status = get_schwab_status()
    assert status['authenticated'] is False
    assert 'error' in status
