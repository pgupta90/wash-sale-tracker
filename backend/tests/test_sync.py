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
        buy_trade = conn.execute("SELECT status FROM trades WHERE id='stock-1'").fetchone()
        sell_trade = conn.execute("SELECT status FROM trades WHERE id='stock-2'").fetchone()
    assert buy_trade['status'] == 'open'
    assert sell_trade['status'] == 'closed'

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

from backend.sync import sync_option_orders

MOCK_OPTION_ORDERS = [
    {
        'id': 'opt-order-1',
        'chain_symbol': 'META',
        'price': '5.50',
        'quantity': '1.00000',
        'state': 'filled',
        'opening_strategy': 'long_call',
        'closing_strategy': None,
        'created_at': '2026-04-15T14:00:00Z',
        'legs': [
            {
                'option': 'https://api.robinhood.com/options/instruments/leg-1/',
                'side': 'buy',
                'position_effect': 'open',
                'ratio_quantity': '1',
            }
        ],
    },
    {
        'id': 'opt-order-2',
        'chain_symbol': 'META',
        'price': '2.00',
        'quantity': '1.00000',
        'state': 'filled',
        'opening_strategy': 'iron_condor',
        'closing_strategy': None,
        'created_at': '2026-04-16T14:00:00Z',
        'legs': [
            {'option': 'https://api.robinhood.com/options/instruments/leg-2/',
             'side': 'sell', 'position_effect': 'open', 'ratio_quantity': '1'},
            {'option': 'https://api.robinhood.com/options/instruments/leg-3/',
             'side': 'buy', 'position_effect': 'open', 'ratio_quantity': '1'},
            {'option': 'https://api.robinhood.com/options/instruments/leg-4/',
             'side': 'sell', 'position_effect': 'open', 'ratio_quantity': '1'},
            {'option': 'https://api.robinhood.com/options/instruments/leg-5/',
             'side': 'buy', 'position_effect': 'open', 'ratio_quantity': '1'},
        ],
    },
]

_INSTRUMENTS = {
    'https://api.robinhood.com/options/instruments/leg-1/':
        {'expiration_date': '2026-06-20', 'strike_price': '600.0000', 'type': 'call'},
    'https://api.robinhood.com/options/instruments/leg-2/':
        {'expiration_date': '2026-06-20', 'strike_price': '610.0000', 'type': 'call'},
    'https://api.robinhood.com/options/instruments/leg-3/':
        {'expiration_date': '2026-06-20', 'strike_price': '620.0000', 'type': 'call'},
    'https://api.robinhood.com/options/instruments/leg-4/':
        {'expiration_date': '2026-06-20', 'strike_price': '580.0000', 'type': 'put'},
    'https://api.robinhood.com/options/instruments/leg-5/':
        {'expiration_date': '2026-06-20', 'strike_price': '570.0000', 'type': 'put'},
}

def test_sync_option_orders_one_row_per_leg(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    with patch('backend.sync.r.orders.get_all_option_orders', return_value=MOCK_OPTION_ORDERS), \
         patch('backend.sync.r.helper.request_get', side_effect=lambda url: _INSTRUMENTS[url]):
        count = sync_option_orders(db_path=db_path)
    # 1 leg (single call) + 4 legs (iron condor) = 5
    assert count == 5
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM trades WHERE trade_type='option'").fetchall()
    assert len(rows) == 5

def test_sync_option_orders_maps_strategy(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    with patch('backend.sync.r.orders.get_all_option_orders', return_value=MOCK_OPTION_ORDERS), \
         patch('backend.sync.r.helper.request_get', side_effect=lambda url: _INSTRUMENTS[url]):
        sync_option_orders(db_path=db_path)
    with get_connection(db_path) as conn:
        single = conn.execute(
            "SELECT strategy FROM trades WHERE id='opt-order-1-leg-0'"
        ).fetchone()
        condor = conn.execute(
            "SELECT strategy FROM trades WHERE id='opt-order-2-leg-0'"
        ).fetchone()
    assert single['strategy'] == 'single'
    assert condor['strategy'] == 'iron_condor'

def test_sync_option_orders_sets_option_type_and_strike(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    with patch('backend.sync.r.orders.get_all_option_orders', return_value=MOCK_OPTION_ORDERS), \
         patch('backend.sync.r.helper.request_get', side_effect=lambda url: _INSTRUMENTS[url]):
        sync_option_orders(db_path=db_path)
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM trades WHERE id='opt-order-1-leg-0'").fetchone()
    assert row['option_type'] == 'call'
    assert row['strike_price'] == 600.0
    assert row['expiration_date'] == '2026-06-20'
