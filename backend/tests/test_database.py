import pytest
from backend.database import init_db, upsert_trade, get_connection, \
    get_last_synced, set_last_synced, search_trades

STOCK_TRADE = {
    'id': 'order-1', 'symbol': 'META', 'platform': 'robinhood',
    'trade_type': 'stock', 'option_type': None, 'strategy': None,
    'side': 'buy', 'expiration_date': None, 'strike_price': None,
    'trade_price': 500.00, 'quantity': 10.0, 'status': 'closed',
    'executed_at': '2026-04-20T10:00:00+00:00',
    'synced_at': '2026-05-04T12:00:00+00:00',
}

OPTION_TRADE = {
    'id': 'opt-1', 'symbol': 'META', 'platform': 'robinhood',
    'trade_type': 'option', 'option_type': 'call', 'strategy': 'single',
    'side': 'buy', 'expiration_date': '2026-06-20', 'strike_price': 600.0,
    'trade_price': 5.50, 'quantity': 1.0, 'status': 'open',
    'executed_at': '2026-04-20T14:00:00+00:00',
    'synced_at': '2026-05-04T12:00:00+00:00',
}

def test_init_db_creates_trades_table(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='trades'"
        ).fetchone()
    assert row is not None

def test_upsert_trade_inserts_stock(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    upsert_trade(STOCK_TRADE, db_path)
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM trades WHERE id = 'order-1'").fetchone()
    assert row['symbol'] == 'META'
    assert row['trade_type'] == 'stock'
    assert row['option_type'] is None
    assert row['strategy'] is None

def test_upsert_trade_no_duplicates_on_resync(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    upsert_trade(STOCK_TRADE, db_path)
    updated = {**STOCK_TRADE, 'status': 'open'}
    upsert_trade(updated, db_path)
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM trades WHERE id = 'order-1'").fetchall()
    assert len(rows) == 1
    assert rows[0]['status'] == 'open'

def test_upsert_trade_stores_option_fields(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    upsert_trade(OPTION_TRADE, db_path)
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM trades WHERE id = 'opt-1'").fetchone()
    assert row['option_type'] == 'call'
    assert row['strike_price'] == 600.0
    assert row['expiration_date'] == '2026-06-20'
    assert row['strategy'] == 'single'

def test_sync_meta_get_set(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    assert get_last_synced(db_path) is None
    set_last_synced('2026-05-04T12:00:00+00:00', db_path)
    assert get_last_synced(db_path) == '2026-05-04T12:00:00+00:00'
    set_last_synced('2026-05-04T13:00:00+00:00', db_path)
    assert get_last_synced(db_path) == '2026-05-04T13:00:00+00:00'

def test_search_trades_filters_by_symbol(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    upsert_trade(OPTION_TRADE, db_path)
    aapl_trade = {**STOCK_TRADE, 'id': 'aapl-1', 'symbol': 'AAPL'}
    upsert_trade(aapl_trade, db_path)
    results = search_trades('META', None, None, db_path=db_path)
    assert len(results) == 1
    assert results[0]['symbol'] == 'META'

def test_search_trades_returns_empty_for_unknown_symbol(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    results = search_trades('ZZZZ', None, None, db_path=db_path)
    assert results == []

def test_search_trades_excludes_trades_outside_search_days(tmp_path):
    db_path = str(tmp_path / "test.sqlite")
    init_db(db_path)
    old_trade = {**STOCK_TRADE, 'id': 'old-1', 'executed_at': '2020-01-01T10:00:00+00:00'}
    upsert_trade(old_trade, db_path)
    results = search_trades('META', None, None, search_days=30, db_path=db_path)
    assert results == []
