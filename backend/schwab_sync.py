from datetime import datetime, timedelta, timezone
from backend.database import upsert_trade
from backend.schwab_auth import get_schwab_client

SYNC_DAYS = 60

INSTRUCTION_MAP = {
    'BUY': 'buy',
    'BUY_TO_OPEN': 'buy',
    'BUY_TO_CLOSE': 'buy',
    'SELL': 'sell',
    'SELL_TO_OPEN': 'sell',
    'SELL_TO_CLOSE': 'sell',
}


def _cutoff_dt() -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=SYNC_DAYS)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_close_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace('+0000', '+00:00'))


def sync_schwab_orders(client=None, db_path: str = None) -> int:
    """Fetch filled orders from Schwab for the last 60 days and upsert into SQLite."""
    if client is None:
        client = get_schwab_client()

    kwargs = {'db_path': db_path} if db_path else {}
    cutoff = _cutoff_dt()
    now = datetime.now(timezone.utc)

    acct_resp = client.get_account_numbers()
    accounts = acct_resp.json()
    account_hash = accounts[0]['hashValue']

    from schwab.client import Client
    orders_resp = client.get_orders_for_account(
        account_hash=account_hash,
        from_entered_datetime=cutoff,
        to_entered_datetime=now,
        status=Client.Order.Status.FILLED,
    )
    orders = orders_resp.json()

    count = 0
    for order in orders:
        close_time = order.get('closeTime')
        if not close_time:
            continue
        executed_dt = _parse_close_time(close_time)
        if executed_dt < cutoff:
            continue

        trade_price = 0.0
        activities = order.get('orderActivityCollection', [])
        if activities:
            exec_legs = activities[0].get('executionLegs', [])
            if exec_legs:
                trade_price = float(exec_legs[0].get('price', 0))

        for leg_idx, leg in enumerate(order.get('orderLegCollection', [])):
            instrument = leg.get('instrument', {})
            asset_type = instrument.get('assetType', '')
            instruction = leg.get('instruction', '')
            raw_symbol = instrument.get('symbol', '')
            symbol = raw_symbol.split(' ')[0].upper()
            put_call = instrument.get('putCall', '')

            trade = {
                'id': f"schwab-{order['orderId']}-{leg_idx}",
                'symbol': symbol,
                'platform': 'schwab',
                'trade_type': 'option' if asset_type == 'OPTION' else 'stock',
                'option_type': put_call.lower() if put_call else None,
                'strategy': None,
                'side': INSTRUCTION_MAP.get(instruction, 'buy'),
                'expiration_date': instrument.get('expirationDate'),
                'strike_price': float(instrument['strikePrice']) if instrument.get('strikePrice') else None,
                'trade_price': trade_price,
                'quantity': float(order.get('filledQuantity', 0)),
                'status': 'closed' if order.get('status') == 'FILLED' else 'open',
                'executed_at': close_time,
                'synced_at': _now_iso(),
            }
            upsert_trade(trade, **kwargs)
            count += 1

    return count
