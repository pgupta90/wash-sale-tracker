import robin_stocks.robinhood as r
from datetime import datetime, timezone
from backend.database import upsert_trade

STATUS_MAP = {
    'filled': 'closed',
    'cancelled': 'closed',
    'rejected': 'closed',
    'confirmed': 'open',
    'unconfirmed': 'open',
    'partially_filled': 'open',
}

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def sync_stock_orders(db_path: str = None) -> int:
    """Fetch all stock orders from Robinhood and upsert into SQLite."""
    kwargs = {'db_path': db_path} if db_path else {}
    orders = r.orders.get_all_stock_orders()
    count = 0
    for order in orders:
        if not order.get('average_price') or not order.get('last_transaction_at'):
            continue
        instrument = r.helper.request_get(order['instrument'])
        trade = {
            'id': order['id'],
            'symbol': instrument.get('symbol', '').upper(),
            'platform': 'robinhood',
            'trade_type': 'stock',
            'option_type': None,
            'strategy': None,
            'side': order['side'],
            'expiration_date': None,
            'strike_price': None,
            'trade_price': float(order['average_price']),
            'quantity': float(order['quantity']),
            'status': STATUS_MAP.get(order['state'], 'closed'),
            'executed_at': order['last_transaction_at'],
            'synced_at': _now_iso(),
        }
        upsert_trade(trade, **kwargs)
        count += 1
    return count
