from datetime import datetime, timezone

_NOW = datetime.now(timezone.utc).isoformat()

# All executed_at dates fall within the last 30 days (Apr 20 – May 20 2026)
# so they are visible under the default search_days: 30 window.

DEMO_TRADES = [
    # ── AAPL ─────────────────────────────────────────────────────────────────
    # Stock: bought Apr 21, sold at loss May 2, bought back May 14 (12 days → wash sale)
    {
        'id': 'demo-aapl-001', 'symbol': 'AAPL', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 236.80, 'quantity': 100.0, 'status': 'open',
        'executed_at': '2026-04-21T14:32:00+00:00',
    },
    {
        'id': 'demo-aapl-002', 'symbol': 'AAPL', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'sell', 'expiration_date': None, 'strike_price': None,
        'trade_price': 219.40, 'quantity': 100.0, 'status': 'closed',
        'executed_at': '2026-05-02T10:15:00+00:00',
    },
    {
        'id': 'demo-aapl-003', 'symbol': 'AAPL', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 224.20, 'quantity': 100.0, 'status': 'open',
        'executed_at': '2026-05-14T11:05:00+00:00',
    },
    # Options: long call opened Apr 23, closed at loss May 8
    {
        'id': 'demo-aapl-004', 'symbol': 'AAPL', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'call', 'strategy': 'single',
        'side': 'buy', 'expiration_date': '2026-06-19', 'strike_price': 225.0,
        'trade_price': 9.80, 'quantity': 2.0, 'status': 'open',
        'executed_at': '2026-04-23T10:20:00+00:00',
    },
    {
        'id': 'demo-aapl-005', 'symbol': 'AAPL', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'call', 'strategy': 'single',
        'side': 'sell', 'expiration_date': '2026-06-19', 'strike_price': 225.0,
        'trade_price': 5.30, 'quantity': 2.0, 'status': 'closed',
        'executed_at': '2026-05-08T14:45:00+00:00',
    },
    # Options: covered call, still open
    {
        'id': 'demo-aapl-006', 'symbol': 'AAPL', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'call', 'strategy': 'single',
        'side': 'sell', 'expiration_date': '2026-07-18', 'strike_price': 245.0,
        'trade_price': 4.60, 'quantity': 1.0, 'status': 'open',
        'executed_at': '2026-05-15T11:30:00+00:00',
    },

    # ── TSLA ─────────────────────────────────────────────────────────────────
    {
        'id': 'demo-tsla-001', 'symbol': 'TSLA', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 262.40, 'quantity': 50.0, 'status': 'open',
        'executed_at': '2026-04-22T13:10:00+00:00',
    },
    {
        'id': 'demo-tsla-002', 'symbol': 'TSLA', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'sell', 'expiration_date': None, 'strike_price': None,
        'trade_price': 278.90, 'quantity': 50.0, 'status': 'closed',
        'executed_at': '2026-05-12T15:45:00+00:00',
    },

    # ── NVDA ─────────────────────────────────────────────────────────────────
    # Post-10:1 split prices ~$108–$135
    # Options: protective put opened Apr 20, closed at profit Apr 30
    {
        'id': 'demo-nvda-004', 'symbol': 'NVDA', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'put', 'strategy': 'single',
        'side': 'buy', 'expiration_date': '2026-06-20', 'strike_price': 125.0,
        'trade_price': 5.60, 'quantity': 5.0, 'status': 'open',
        'executed_at': '2026-04-20T09:10:00+00:00',
    },
    {
        'id': 'demo-nvda-005', 'symbol': 'NVDA', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'put', 'strategy': 'single',
        'side': 'sell', 'expiration_date': '2026-06-20', 'strike_price': 125.0,
        'trade_price': 10.80, 'quantity': 5.0, 'status': 'closed',
        'executed_at': '2026-04-30T13:55:00+00:00',
    },
    # Stock: bought Apr 22, sold at loss May 5, bought back May 16 (11 days → wash sale)
    {
        'id': 'demo-nvda-001', 'symbol': 'NVDA', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 131.50, 'quantity': 150.0, 'status': 'open',
        'executed_at': '2026-04-22T09:55:00+00:00',
    },
    {
        'id': 'demo-nvda-002', 'symbol': 'NVDA', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'sell', 'expiration_date': None, 'strike_price': None,
        'trade_price': 112.80, 'quantity': 150.0, 'status': 'closed',
        'executed_at': '2026-05-05T14:20:00+00:00',
    },
    {
        'id': 'demo-nvda-003', 'symbol': 'NVDA', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 118.40, 'quantity': 150.0, 'status': 'open',
        'executed_at': '2026-05-16T10:30:00+00:00',
    },
    # Options: cash-secured put, still open
    {
        'id': 'demo-nvda-006', 'symbol': 'NVDA', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'put', 'strategy': 'single',
        'side': 'sell', 'expiration_date': '2026-06-20', 'strike_price': 108.0,
        'trade_price': 4.20, 'quantity': 5.0, 'status': 'open',
        'executed_at': '2026-05-17T10:05:00+00:00',
    },

    # ── SPY — Iron Condor ─────────────────────────────────────────────────────
    # Opened May 1 2026, SPY at ~$522. Expiry Jul 18 2026.
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
    # Stock: bought Apr 21, sold at loss May 4, bought back May 15 (11 days → wash sale)
    {
        'id': 'demo-meta-003', 'symbol': 'META', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 628.40, 'quantity': 20.0, 'status': 'open',
        'executed_at': '2026-04-21T10:45:00+00:00',
    },
    {
        'id': 'demo-meta-004', 'symbol': 'META', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'sell', 'expiration_date': None, 'strike_price': None,
        'trade_price': 596.80, 'quantity': 20.0, 'status': 'closed',
        'executed_at': '2026-05-04T14:10:00+00:00',
    },
    {
        'id': 'demo-meta-005', 'symbol': 'META', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 603.20, 'quantity': 25.0, 'status': 'open',
        'executed_at': '2026-05-15T09:30:00+00:00',
    },
    # Options: short put opened May 1, closed at loss May 14
    {
        'id': 'demo-meta-001', 'symbol': 'META', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'put', 'strategy': 'single',
        'side': 'sell', 'expiration_date': '2026-08-21', 'strike_price': 600.0,
        'trade_price': 12.80, 'quantity': 2.0, 'status': 'open',
        'executed_at': '2026-05-01T11:30:00+00:00',
    },
    {
        'id': 'demo-meta-002', 'symbol': 'META', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'put', 'strategy': 'single',
        'side': 'buy', 'expiration_date': '2026-08-21', 'strike_price': 600.0,
        'trade_price': 21.50, 'quantity': 2.0, 'status': 'closed',
        'executed_at': '2026-05-14T09:45:00+00:00',
    },

    # ── MSFT call spread ──────────────────────────────────────────────────────
    {
        'id': 'demo-msft-001', 'symbol': 'MSFT', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'call', 'strategy': 'call_spread',
        'side': 'buy', 'expiration_date': '2026-08-21', 'strike_price': 420.0,
        'trade_price': 8.50, 'quantity': 1.0, 'status': 'open',
        'executed_at': '2026-04-25T13:00:00+00:00',
    },
    {
        'id': 'demo-msft-002', 'symbol': 'MSFT', 'platform': 'robinhood',
        'trade_type': 'option', 'option_type': 'call', 'strategy': 'call_spread',
        'side': 'sell', 'expiration_date': '2026-08-21', 'strike_price': 440.0,
        'trade_price': 3.20, 'quantity': 1.0, 'status': 'open',
        'executed_at': '2026-04-25T13:00:00+00:00',
    },

    # ── AMZN ─────────────────────────────────────────────────────────────────
    # Wash sale: bought Apr 20, sold at loss May 3, bought back May 17 (14 days → wash sale)
    {
        'id': 'demo-amzn-001', 'symbol': 'AMZN', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 193.50, 'quantity': 30.0, 'status': 'open',
        'executed_at': '2026-04-20T10:05:00+00:00',
    },
    {
        'id': 'demo-amzn-002', 'symbol': 'AMZN', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'sell', 'expiration_date': None, 'strike_price': None,
        'trade_price': 180.20, 'quantity': 30.0, 'status': 'closed',
        'executed_at': '2026-05-03T11:20:00+00:00',
    },
    {
        'id': 'demo-amzn-003', 'symbol': 'AMZN', 'platform': 'robinhood',
        'trade_type': 'stock', 'option_type': None, 'strategy': None,
        'side': 'buy', 'expiration_date': None, 'strike_price': None,
        'trade_price': 186.80, 'quantity': 25.0, 'status': 'open',
        'executed_at': '2026-05-17T14:00:00+00:00',
    },

    # ── QQQ — Iron Butterfly ──────────────────────────────────────────────────
    # Opened May 2 2026, QQQ at ~$462. Expiry Jul 18 2026.
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
