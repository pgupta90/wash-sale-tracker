from datetime import datetime, timezone

_NOW = datetime.now(timezone.utc).isoformat()

DEMO_TRADES = [
    # ── AAPL ─────────────────────────────────────────────────────────────────
    # Stock: bought Feb 3, sold at loss Mar 10, bought back Mar 26 (16 days → wash sale)
    {
        'id': 'demo-aapl-001', 'symbol': 'AAPL', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 238.50, 'quantity': 100.0, 'status': 'open',
        'executed_at': '2026-02-03T14:32:00+00:00',
    },
    {
        'id': 'demo-aapl-002', 'symbol': 'AAPL', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'sell', 'expiration_date': None, 'strike_price': None,
        'trade_price': 218.90, 'quantity': 100.0, 'status': 'closed',
        'executed_at': '2026-03-10T10:15:00+00:00',
    },
    {
        'id': 'demo-aapl-003', 'symbol': 'AAPL', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 224.70, 'quantity': 100.0, 'status': 'open',
        'executed_at': '2026-03-26T11:05:00+00:00',
    },
    # Options: long call opened Feb 15, closed at loss Apr 8
    {
        'id': 'demo-aapl-004', 'symbol': 'AAPL', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'call', 'strategy': 'single',
        'side': 'buy', 'expiration_date': '2026-06-19', 'strike_price': 225.0,
        'trade_price': 9.80, 'quantity': 2.0, 'status': 'open',
        'executed_at': '2026-02-15T10:20:00+00:00',
    },
    {
        'id': 'demo-aapl-005', 'symbol': 'AAPL', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'call', 'strategy': 'single',
        'side': 'sell', 'expiration_date': '2026-06-19', 'strike_price': 225.0,
        'trade_price': 5.30, 'quantity': 2.0, 'status': 'closed',
        'executed_at': '2026-04-08T14:45:00+00:00',
    },
    # Options: covered call written against stock position, still open
    {
        'id': 'demo-aapl-006', 'symbol': 'AAPL', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'call', 'strategy': 'single',
        'side': 'sell', 'expiration_date': '2026-07-18', 'strike_price': 245.0,
        'trade_price': 4.60, 'quantity': 1.0, 'status': 'open',
        'executed_at': '2026-04-22T11:30:00+00:00',
    },

    # ── TSLA ─────────────────────────────────────────────────────────────────
    {
        'id': 'demo-tsla-001', 'symbol': 'TSLA', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 245.30, 'quantity': 50.0, 'status': 'open',
        'executed_at': '2025-11-20T13:10:00+00:00',
    },
    {
        'id': 'demo-tsla-002', 'symbol': 'TSLA', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'sell', 'expiration_date': None, 'strike_price': None,
        'trade_price': 258.60, 'quantity': 50.0, 'status': 'closed',
        'executed_at': '2025-12-28T15:45:00+00:00',
    },

    # ── NVDA ─────────────────────────────────────────────────────────────────
    # Post-10:1 split (Jun 2024) prices ~$105–$135
    # Options: protective put opened Feb 20, closed at profit Mar 12
    {
        'id': 'demo-nvda-004', 'symbol': 'NVDA', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'put', 'strategy': 'single',
        'side': 'buy', 'expiration_date': '2026-03-20', 'strike_price': 130.0,
        'trade_price': 5.60, 'quantity': 5.0, 'status': 'open',
        'executed_at': '2026-02-20T09:10:00+00:00',
    },
    {
        'id': 'demo-nvda-005', 'symbol': 'NVDA', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'put', 'strategy': 'single',
        'side': 'sell', 'expiration_date': '2026-03-20', 'strike_price': 130.0,
        'trade_price': 10.80, 'quantity': 5.0, 'status': 'closed',
        'executed_at': '2026-03-12T13:55:00+00:00',
    },
    # Stock: bought Mar 5, sold at loss Apr 7, bought back Apr 20 (13 days → wash sale)
    {
        'id': 'demo-nvda-001', 'symbol': 'NVDA', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 132.80, 'quantity': 150.0, 'status': 'open',
        'executed_at': '2026-03-05T09:55:00+00:00',
    },
    {
        'id': 'demo-nvda-002', 'symbol': 'NVDA', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'sell', 'expiration_date': None, 'strike_price': None,
        'trade_price': 112.40, 'quantity': 150.0, 'status': 'closed',
        'executed_at': '2026-04-07T14:20:00+00:00',
    },
    {
        'id': 'demo-nvda-003', 'symbol': 'NVDA', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 118.60, 'quantity': 150.0, 'status': 'open',
        'executed_at': '2026-04-20T10:30:00+00:00',
    },
    # Options: cash-secured put, still open
    {
        'id': 'demo-nvda-006', 'symbol': 'NVDA', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'put', 'strategy': 'single',
        'side': 'sell', 'expiration_date': '2026-06-20', 'strike_price': 110.0,
        'trade_price': 4.20, 'quantity': 5.0, 'status': 'open',
        'executed_at': '2026-04-25T10:05:00+00:00',
    },

    # ── SPY — Iron Condor ─────────────────────────────────────────────────────
    # Opened May 1 2026, SPY at ~$522. Expiry Jul 18 2026.
    # Short $490/$480 put spread + short $555/$565 call spread.
    # Net credit: (4.20 + 3.80) − (2.80 + 2.10) = $3.10/share
    {
        'id': 'demo-spy-001', 'symbol': 'SPY', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'put', 'strategy': 'iron_condor',
        'side': 'sell', 'expiration_date': '2026-07-18', 'strike_price': 490.0,
        'trade_price': 4.20, 'quantity': 2.0, 'status': 'open',
        'executed_at': '2026-05-01T10:00:00+00:00',
    },
    {
        'id': 'demo-spy-002', 'symbol': 'SPY', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'put', 'strategy': 'iron_condor',
        'side': 'buy', 'expiration_date': '2026-07-18', 'strike_price': 480.0,
        'trade_price': 2.80, 'quantity': 2.0, 'status': 'open',
        'executed_at': '2026-05-01T10:00:00+00:00',
    },
    {
        'id': 'demo-spy-003', 'symbol': 'SPY', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'call', 'strategy': 'iron_condor',
        'side': 'sell', 'expiration_date': '2026-07-18', 'strike_price': 555.0,
        'trade_price': 3.80, 'quantity': 2.0, 'status': 'open',
        'executed_at': '2026-05-01T10:00:00+00:00',
    },
    {
        'id': 'demo-spy-004', 'symbol': 'SPY', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'call', 'strategy': 'iron_condor',
        'side': 'buy', 'expiration_date': '2026-07-18', 'strike_price': 565.0,
        'trade_price': 2.10, 'quantity': 2.0, 'status': 'open',
        'executed_at': '2026-05-01T10:00:00+00:00',
    },

    # ── META ─────────────────────────────────────────────────────────────────
    # Stock: bought Feb 5, sold at loss Mar 18, bought back Apr 2 (15 days → wash sale)
    # META trading ~$595–$645 in Feb–Apr 2026
    {
        'id': 'demo-meta-003', 'symbol': 'META', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 628.40, 'quantity': 20.0, 'status': 'open',
        'executed_at': '2026-02-05T10:45:00+00:00',
    },
    {
        'id': 'demo-meta-004', 'symbol': 'META', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'sell', 'expiration_date': None, 'strike_price': None,
        'trade_price': 596.80, 'quantity': 20.0, 'status': 'closed',
        'executed_at': '2026-03-18T14:10:00+00:00',
    },
    {
        'id': 'demo-meta-005', 'symbol': 'META', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 604.50, 'quantity': 25.0, 'status': 'open',
        'executed_at': '2026-04-02T09:30:00+00:00',
    },
    # Options: short put opened Apr 1, closed at loss Apr 28
    {
        'id': 'demo-meta-001', 'symbol': 'META', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'put', 'strategy': 'single',
        'side': 'sell', 'expiration_date': '2026-08-21', 'strike_price': 600.0,
        'trade_price': 12.80, 'quantity': 2.0, 'status': 'open',
        'executed_at': '2026-04-01T11:30:00+00:00',
    },
    {
        'id': 'demo-meta-002', 'symbol': 'META', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'put', 'strategy': 'single',
        'side': 'buy', 'expiration_date': '2026-08-21', 'strike_price': 600.0,
        'trade_price': 21.50, 'quantity': 2.0, 'status': 'closed',
        'executed_at': '2026-04-28T09:45:00+00:00',
    },

    # ── MSFT call spread ──────────────────────────────────────────────────────
    {
        'id': 'demo-msft-001', 'symbol': 'MSFT', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'call', 'strategy': 'call_spread',
        'side': 'buy', 'expiration_date': '2026-04-17', 'strike_price': 420.0,
        'trade_price': 8.50, 'quantity': 1.0, 'status': 'open',
        'executed_at': '2026-01-15T13:00:00+00:00',
    },
    {
        'id': 'demo-msft-002', 'symbol': 'MSFT', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'call', 'strategy': 'call_spread',
        'side': 'sell', 'expiration_date': '2026-04-17', 'strike_price': 440.0,
        'trade_price': 3.20, 'quantity': 1.0, 'status': 'open',
        'executed_at': '2026-01-15T13:00:00+00:00',
    },

    # ── AMZN ─────────────────────────────────────────────────────────────────
    # Wash sale scenario: sold at loss Feb 12, bought back within 30 days
    {
        'id': 'demo-amzn-001', 'symbol': 'AMZN', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 195.20, 'quantity': 30.0, 'status': 'open',
        'executed_at': '2026-01-03T10:05:00+00:00',
    },
    {
        'id': 'demo-amzn-002', 'symbol': 'AMZN', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'sell', 'expiration_date': None, 'strike_price': None,
        'trade_price': 182.60, 'quantity': 30.0, 'status': 'closed',
        'executed_at': '2026-02-12T11:20:00+00:00',
    },
    # Bought back 17 days later — potential wash sale!
    {
        'id': 'demo-amzn-003', 'symbol': 'AMZN', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 188.40, 'quantity': 25.0, 'status': 'open',
        'executed_at': '2026-03-01T14:00:00+00:00',
    },

    # ── QQQ — Iron Butterfly ──────────────────────────────────────────────────
    # Opened May 2 2026, QQQ at ~$462. Expiry Jul 18 2026.
    # ATM $460 put + ATM $460 call sold; $440 put + $480 call bought as wings.
    # Net credit: (8.50 + 8.20) − (3.20 + 3.50) = $10.00/share
    {
        'id': 'demo-qqq-001', 'symbol': 'QQQ', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'put', 'strategy': 'iron_butterfly',
        'side': 'sell', 'expiration_date': '2026-07-18', 'strike_price': 460.0,
        'trade_price': 8.50, 'quantity': 2.0, 'status': 'open',
        'executed_at': '2026-05-02T09:30:00+00:00',
    },
    {
        'id': 'demo-qqq-002', 'symbol': 'QQQ', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'put', 'strategy': 'iron_butterfly',
        'side': 'buy', 'expiration_date': '2026-07-18', 'strike_price': 440.0,
        'trade_price': 3.20, 'quantity': 2.0, 'status': 'open',
        'executed_at': '2026-05-02T09:30:00+00:00',
    },
    {
        'id': 'demo-qqq-003', 'symbol': 'QQQ', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'call', 'strategy': 'iron_butterfly',
        'side': 'sell', 'expiration_date': '2026-07-18', 'strike_price': 460.0,
        'trade_price': 8.20, 'quantity': 2.0, 'status': 'open',
        'executed_at': '2026-05-02T09:30:00+00:00',
    },
    {
        'id': 'demo-qqq-004', 'symbol': 'QQQ', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'call', 'strategy': 'iron_butterfly',
        'side': 'buy', 'expiration_date': '2026-07-18', 'strike_price': 480.0,
        'trade_price': 3.50, 'quantity': 2.0, 'status': 'open',
        'executed_at': '2026-05-02T09:30:00+00:00',
    },
]
