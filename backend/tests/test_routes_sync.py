from unittest.mock import patch
from fastapi.testclient import TestClient

def get_client():
    with patch('backend.main.login_from_config'):
        from backend.main import app
        return TestClient(app)

def test_sync_status_never_synced():
    client = get_client()
    with patch('backend.routes.sync.get_last_synced', return_value=None):
        response = client.get('/sync/status')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'idle'
    assert data['last_synced'] is None

def test_sync_status_shows_timestamp():
    client = get_client()
    with patch('backend.routes.sync.get_last_synced', return_value='2026-05-04T12:00:00+00:00'):
        response = client.get('/sync/status')
    assert response.status_code == 200
    assert response.json()['last_synced'] == '2026-05-04T12:00:00+00:00'

def test_post_sync_calls_both_syncs():
    client = get_client()
    with patch('backend.routes.sync.sync_stock_orders', return_value=10) as ms, \
         patch('backend.routes.sync.sync_option_orders', return_value=5) as mo, \
         patch('backend.routes.sync.set_last_synced') as mset, \
         patch('backend.routes.sync.get_last_synced', return_value='2026-05-04T12:00:00+00:00'):
        response = client.post('/sync')
    assert response.status_code == 200
    assert response.json()['status'] == 'idle'
    ms.assert_called_once()
    mo.assert_called_once()
    mset.assert_called_once()
