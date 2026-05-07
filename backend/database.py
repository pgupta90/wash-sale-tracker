import sqlite3
import os
from contextlib import contextmanager
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), 'db.sqlite')

@contextmanager
def get_connection(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db(db_path: str = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                platform TEXT NOT NULL DEFAULT 'robinhood',
                trade_type TEXT NOT NULL,
                option_type TEXT,
                strategy TEXT,
                side TEXT NOT NULL,
                expiration_date TEXT,
                strike_price REAL,
                trade_price REAL NOT NULL,
                quantity REAL NOT NULL,
                status TEXT NOT NULL,
                executed_at TEXT NOT NULL,
                synced_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

def upsert_trade(trade: dict, db_path: str = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO trades (
                id, symbol, platform, trade_type, option_type, strategy,
                side, expiration_date, strike_price, trade_price,
                quantity, status, executed_at, synced_at
            ) VALUES (
                :id, :symbol, :platform, :trade_type, :option_type, :strategy,
                :side, :expiration_date, :strike_price, :trade_price,
                :quantity, :status, :executed_at, :synced_at
            )
            ON CONFLICT(id) DO UPDATE SET
                status=excluded.status,
                synced_at=excluded.synced_at,
                trade_price=excluded.trade_price,
                quantity=excluded.quantity
        """, trade)

def get_last_synced(db_path: str = DB_PATH) -> Optional[str]:
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT value FROM sync_meta WHERE key = 'last_synced'"
        ).fetchone()
        return row['value'] if row else None

def set_last_synced(timestamp: str, db_path: str = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO sync_meta (key, value) VALUES ('last_synced', ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (timestamp,))

def get_schwab_last_synced(db_path: str = DB_PATH) -> Optional[str]:
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT value FROM sync_meta WHERE key = 'schwab_last_synced'"
        ).fetchone()
        return row['value'] if row else None

def set_schwab_last_synced(timestamp: str, db_path: str = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO sync_meta (key, value) VALUES ('schwab_last_synced', ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (timestamp,))

def search_trades(
    symbol: str,
    expiry: Optional[str],
    strike: Optional[float],
    search_days: int = 30,
    db_path: str = DB_PATH,
) -> list:
    # SQLite compares lexicographically; this works because timestamps
    # are UTC ISO 8601 strings which sort correctly.
    query = f"""
        SELECT * FROM trades
        WHERE symbol = ?
        AND executed_at >= datetime('now', '-{int(search_days)} days')
    """
    params: list = [symbol.upper()]
    if expiry:
        query += " AND expiration_date = ?"
        params.append(expiry)
    if strike is not None:
        query += " AND strike_price = ?"
        params.append(strike)
    query += " ORDER BY executed_at DESC"
    with get_connection(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
