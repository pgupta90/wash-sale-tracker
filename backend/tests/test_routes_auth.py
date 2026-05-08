from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

def get_client(follow_redirects=True):
    with patch('backend.main.login_from_config'), \
         patch('backend.main.get_schwab_status', return_value={'authenticated': False}):
        from backend.main import app
        return TestClient(app, follow_redirects=follow_redirects)

def test_auth_status_authenticated():
    client = get_client()
    with patch('backend.auth.r.account.load_account_profile', return_value={'username': 'u'}):
        response = client.get('/auth/status')
    assert response.status_code == 200
    assert response.json()['authenticated'] is True

def test_auth_status_unauthenticated():
    client = get_client()
    with patch('backend.auth.r.account.load_account_profile', side_effect=Exception("not logged in")):
        response = client.get('/auth/status')
    assert response.status_code == 200
    assert response.json()['authenticated'] is False


# Schwab OAuth tests

def test_schwab_connect_returns_url(mock_config):
    client = get_client()
    resp = client.get('/auth/schwab/connect')
    assert resp.status_code == 200
    data = resp.json()
    assert 'url' in data
    assert 'api.schwabapi.com' in data['url']
    assert 'response_type=code' in data['url']
    assert 'dummy_client_id' in data['url']

def test_schwab_callback_success_redirects(mock_config):
    import backend.routes.auth as auth_module
    client = get_client(follow_redirects=False)

    test_state = 'test_state_value'
    auth_module._pending_states.add(test_state)

    mock_token = {
        'access_token': 'tok_abc',
        'refresh_token': 'ref_abc',
        'token_type': 'Bearer',
        'expires_in': 1800,
    }
    with patch('backend.routes.auth.httpx.post') as mock_post, \
         patch('backend.routes.auth.open', create=True), \
         patch('backend.routes.auth.os.makedirs'), \
         patch('backend.routes.auth.os.replace'):
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_token
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        resp = client.get(f'/auth/schwab/callback?code=abc123&state={test_state}')

    assert resp.status_code in (302, 307)
    assert 'schwab=connected' in resp.headers['location']

def test_schwab_callback_rejects_invalid_state(mock_config):
    client = get_client(follow_redirects=False)
    resp = client.get('/auth/schwab/callback?code=abc123&state=invalid_state')
    assert resp.status_code in (302, 307)
    assert 'schwab=error' in resp.headers['location']

def test_schwab_callback_failure_redirects_with_error(mock_config):
    import backend.routes.auth as auth_module
    client = get_client(follow_redirects=False)

    test_state = 'test_state_failure'
    auth_module._pending_states.add(test_state)

    with patch('backend.routes.auth.httpx.post') as mock_post, \
         patch('backend.routes.auth.os.makedirs'):
        mock_post.side_effect = Exception('token exchange failed')
        resp = client.get(f'/auth/schwab/callback?code=bad&state={test_state}')

    assert resp.status_code in (302, 307)
    assert 'schwab=error' in resp.headers['location']
