from unittest.mock import MagicMock
from backend.schwab_sync import sync_schwab_orders
from backend.database import init_db, get_connection

MOCK_ACCOUNT_NUMBERS = [{'accountNumber': '12345678', 'hashValue': 'hash-abc-123'}]

MOCK_STOCK_ORDER = {
    'orderId': 11111,
    'status': 'FILLED',
    'filledQuantity': 10.0,
    'closeTime': '2026-04-20T10:00:00+0000',
    'orderLegCollection': [{
        'instruction': 'BUY',
        'quantity': 10.0,
        'instrument': {'symbol': 'AAPL', 'assetType': 'EQUITY'},
    }],
    'orderActivityCollection': [{
        'executionType': 'FILL',
        'executionLegs': [{'price': 175.50, 'quantity': 10.0}],
    }],
}

MOCK_OPTION_ORDER = {
    'orderId': 22222,
    'status': 'FILLED',
    'filledQuantity': 1.0,
    'closeTime': '2026-04-21T14:00:00+0000',
    'orderLegCollection': [{
        'instruction': 'BUY_TO_OPEN',
        'quantity': 1.0,
        'instrument': {
            'symbol': 'AAPL 260620C00175000',
            'assetType': 'OPTION',
            'putCall': 'CALL',
            'strikePrice': 175.0,
            'expirationDate': '2026-06-20',
        },
    }],
    'orderActivityCollection': [{
        'executionType': 'FILL',
        'executionLegs': [{'price': 5.50, 'quantity': 1.0}],
    }],
}


def _make_client(orders):
    client = MagicMock()
    acct_resp = MagicMock()
    acct_resp.json.return_value = MOCK_ACCOUNT_NUMBERS
    client.get_account_numbers.return_value = acct_resp
    orders_resp = MagicMock()
    orders_resp.json.return_value = orders
    client.get_orders_for_account.return_value = orders_resp
    return client


def test_sync_schwab_stock_order_stored(tmp_path):
    db_path = str(tmp_path / 'test.sqlite')
    init_db(db_path)
    client = _make_client([MOCK_STOCK_ORDER])
    count = sync_schwab_orders(client=client, db_path=db_path)
    assert count == 1
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM trades WHERE id='schwab-11111-0'").fetchone()
    assert row['symbol'] == 'AAPL'
    assert row['platform'] == 'schwab'
    assert row['trade_type'] == 'stock'
    assert row['side'] == 'buy'
    assert row['trade_price'] == 175.50
    assert row['quantity'] == 10.0
    assert row['status'] == 'closed'
    assert row['option_type'] is None


def test_sync_schwab_option_order_stored(tmp_path):
    db_path = str(tmp_path / 'test.sqlite')
    init_db(db_path)
    client = _make_client([MOCK_OPTION_ORDER])
    count = sync_schwab_orders(client=client, db_path=db_path)
    assert count == 1
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM trades WHERE id='schwab-22222-0'").fetchone()
    assert row['symbol'] == 'AAPL'
    assert row['trade_type'] == 'option'
    assert row['option_type'] == 'call'
    assert row['strike_price'] == 175.0
    assert row['expiration_date'] == '2026-06-20'
    assert row['side'] == 'buy'


def test_sync_schwab_sell_instruction(tmp_path):
    db_path = str(tmp_path / 'test.sqlite')
    init_db(db_path)
    sell_order = dict(MOCK_STOCK_ORDER)
    sell_order['orderId'] = 33333
    sell_order['orderLegCollection'] = [{
        **MOCK_STOCK_ORDER['orderLegCollection'][0],
        'instruction': 'SELL',
    }]
    client = _make_client([sell_order])
    sync_schwab_orders(client=client, db_path=db_path)
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT side FROM trades WHERE id='schwab-33333-0'").fetchone()
    assert row['side'] == 'sell'


def test_sync_schwab_no_duplicates(tmp_path):
    db_path = str(tmp_path / 'test.sqlite')
    init_db(db_path)
    client = _make_client([MOCK_STOCK_ORDER])
    sync_schwab_orders(client=client, db_path=db_path)
    client2 = _make_client([MOCK_STOCK_ORDER])
    sync_schwab_orders(client=client2, db_path=db_path)
    with get_connection(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
    assert count == 1


def test_sync_schwab_skips_old_orders(tmp_path):
    db_path = str(tmp_path / 'test.sqlite')
    init_db(db_path)
    old_order = dict(MOCK_STOCK_ORDER)
    old_order['orderId'] = 99999
    old_order['closeTime'] = '2020-01-01T10:00:00+0000'
    client = _make_client([old_order])
    count = sync_schwab_orders(client=client, db_path=db_path)
    assert count == 0


def test_sync_schwab_multi_leg_order(tmp_path):
    db_path = str(tmp_path / 'test.sqlite')
    init_db(db_path)
    multi_leg_order = {
        'orderId': 44444,
        'status': 'FILLED',
        'filledQuantity': 2.0,
        'closeTime': '2026-04-22T10:00:00+0000',
        'orderLegCollection': [
            {'instruction': 'BUY', 'quantity': 1.0, 'instrument': {'symbol': 'AAPL', 'assetType': 'EQUITY'}},
            {'instruction': 'SELL', 'quantity': 1.0, 'instrument': {'symbol': 'MSFT', 'assetType': 'EQUITY'}},
        ],
        'orderActivityCollection': [{'executionType': 'FILL', 'executionLegs': [{'price': 100.0, 'quantity': 2.0}]}],
    }
    client = _make_client([multi_leg_order])
    count = sync_schwab_orders(client=client, db_path=db_path)
    assert count == 2
    with get_connection(db_path) as conn:
        row0 = conn.execute("SELECT * FROM trades WHERE id='schwab-44444-0'").fetchone()
        row1 = conn.execute("SELECT * FROM trades WHERE id='schwab-44444-1'").fetchone()
    assert row0['symbol'] == 'AAPL'
    assert row0['side'] == 'buy'
    assert row0['quantity'] == 1.0
    assert row1['symbol'] == 'MSFT'
    assert row1['side'] == 'sell'
    assert row1['quantity'] == 1.0
