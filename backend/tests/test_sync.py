from unittest.mock import patch
from backend.sync import sync_stock_orders
from backend.database import init_db, get_connection

MOCK_STOCK_ORDERS = [
    {
        'id': 'stock-1',
        'instrument': 'https://api.robinhood.com/instruments/abc/',
        'side': 'buy',
        'average_price': '500.00',
        'quantity': '10.00000',
        'state': 'filled',
        'last_transaction_at': '2026-04-20T10:00:00Z',
    },
    {
        'id': 'stock-2',
        'instrument': 'https://api.robinhood.com/instruments/abc/',
        'side': 'sell',
        'average_price': '510.00',
        'quantity': '5.00000',
        'state': 'cancelled',
        'last_transaction_at': '2026-04-21T11:00:00Z',
    },
]

MOCK_INSTRUMENT = {'symbol': 'META'}

def test_sync_stock_orders_stores_trades(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    with patch('backend.sync.r.orders.get_all_stock_orders', return_value=MOCK_STOCK_ORDERS), \
         patch('backend.sync.r.helper.request_get', return_value=MOCK_INSTRUMENT):
        count = sync_stock_orders(db_path=db_path)
    assert count == 2
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM trades WHERE trade_type='stock'").fetchall()
    assert len(rows) == 2
    assert rows[0]['symbol'] == 'META'
    assert rows[0]['option_type'] is None
    assert rows[0]['strategy'] is None

def test_sync_stock_orders_maps_status(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    with patch('backend.sync.r.orders.get_all_stock_orders', return_value=MOCK_STOCK_ORDERS), \
         patch('backend.sync.r.helper.request_get', return_value=MOCK_INSTRUMENT):
        sync_stock_orders(db_path=db_path)
    with get_connection(db_path) as conn:
        filled = conn.execute("SELECT status FROM trades WHERE id='stock-1'").fetchone()
        cancelled = conn.execute("SELECT status FROM trades WHERE id='stock-2'").fetchone()
    assert filled['status'] == 'closed'
    assert cancelled['status'] == 'closed'

def test_sync_stock_orders_no_duplicates(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    with patch('backend.sync.r.orders.get_all_stock_orders', return_value=MOCK_STOCK_ORDERS), \
         patch('backend.sync.r.helper.request_get', return_value=MOCK_INSTRUMENT):
        sync_stock_orders(db_path=db_path)
        sync_stock_orders(db_path=db_path)
    with get_connection(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
    assert count == 2
