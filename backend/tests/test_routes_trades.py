from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

MOCK_TRADE = {
    'id': 'opt-1', 'symbol': 'META', 'platform': 'robinhood',
    'trade_type': 'option', 'option_type': 'call', 'strategy': 'single',
    'side': 'buy', 'expiration_date': '2026-06-20', 'strike_price': 600.0,
    'trade_price': 5.50, 'quantity': 1.0, 'status': 'open',
    'executed_at': '2026-04-20T10:00:00Z', 'synced_at': '2026-05-04T12:00:00Z',
}

def test_get_trades_requires_symbol():
    response = client.get('/trades')
    assert response.status_code == 422

def test_get_trades_returns_results():
    with patch('backend.routes.trades.search_trades', return_value=[MOCK_TRADE]):
        response = client.get('/trades?symbol=META')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['symbol'] == 'META'

def test_get_trades_passes_all_filters():
    with patch('backend.routes.trades.search_trades', return_value=[]) as mock_search:
        client.get('/trades?symbol=META&expiry=2026-06-20&strike=600.0')
    mock_search.assert_called_once_with(
        symbol='META', expiry='2026-06-20', strike=600.0
    )

def test_get_trades_empty_result():
    with patch('backend.routes.trades.search_trades', return_value=[]):
        response = client.get('/trades?symbol=ZZZZ')
    assert response.status_code == 200
    assert response.json() == []
