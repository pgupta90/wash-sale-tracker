from unittest.mock import patch
from backend.auth import login, get_auth_status

def test_login_success():
    with patch('backend.auth.r.login') as mock_login, \
         patch('backend.auth.r.account.load_account_profile') as mock_profile:
        mock_login.return_value = {'access_token': 'fake-token'}
        mock_profile.return_value = {'username': 'test@test.com'}
        result = login('test@test.com', 'pass')
    assert result['authenticated'] is True
    mock_login.assert_called_once_with(
        username='test@test.com',
        password='pass',
        store_session=True,
        by_sms=False,
    )

def test_login_failure_returns_error():
    with patch('backend.auth.r.login') as mock_login:
        mock_login.side_effect = Exception("Invalid credentials")
        result = login('bad@test.com', 'wrong')
    assert result['authenticated'] is False
    assert 'error' in result

def test_get_auth_status_authenticated():
    with patch('backend.auth.r.account.load_account_profile') as mock_profile:
        mock_profile.return_value = {'username': 'test@test.com'}
        status = get_auth_status()
    assert status['authenticated'] is True

def test_get_auth_status_unauthenticated():
    with patch('backend.auth.r.account.load_account_profile') as mock_profile:
        mock_profile.side_effect = Exception("Not logged in")
        status = get_auth_status()
    assert status['authenticated'] is False
