from unittest.mock import patch
from fastapi.testclient import TestClient

def get_client():
    with patch('backend.main.login_from_config'):
        from backend.main import app
        return TestClient(app)

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
