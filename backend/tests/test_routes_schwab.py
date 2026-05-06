from unittest.mock import patch
from fastapi.testclient import TestClient


def get_client():
    with patch('backend.main.login_from_config'), \
         patch('backend.main.get_schwab_status', return_value={'authenticated': False}):
        from backend.main import app
        return TestClient(app)


def test_schwab_auth_status_unauthenticated():
    client = get_client()
    with patch('backend.routes.auth.get_schwab_status', return_value={'authenticated': False, 'error': 'no token'}):
        response = client.get('/auth/schwab/status')
    assert response.status_code == 200
    data = response.json()
    assert data['authenticated'] is False


def test_schwab_auth_status_authenticated():
    client = get_client()
    with patch('backend.routes.auth.get_schwab_status', return_value={'authenticated': True}):
        response = client.get('/auth/schwab/status')
    assert response.status_code == 200
    assert response.json()['authenticated'] is True


def test_schwab_sync_status_never_synced():
    client = get_client()
    with patch('backend.routes.sync.get_schwab_last_synced', return_value=None):
        response = client.get('/sync/schwab/status')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'idle'
    assert data['last_synced'] is None


def test_post_schwab_sync_calls_sync_function():
    client = get_client()
    with patch('backend.routes.sync.sync_schwab_orders', return_value=5) as mock_sync, \
         patch('backend.routes.sync.set_schwab_last_synced') as mock_set, \
         patch('backend.routes.sync.get_schwab_last_synced', return_value='2026-05-06T12:00:00+00:00'):
        response = client.post('/sync/schwab')
    assert response.status_code == 200
    assert response.json()['status'] == 'idle'
    mock_sync.assert_called_once()
    mock_set.assert_called_once()
