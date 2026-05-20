from pydantic import BaseModel
from typing import Optional

class AuthStatus(BaseModel):
    authenticated: bool
    error: Optional[str] = None

class SyncStatus(BaseModel):
    status: str
    last_synced: Optional[str] = None
    error: Optional[str] = None

class Trade(BaseModel):
    id: str
    symbol: str
    platform: str
    trade_type: str
    option_type: Optional[str] = None
    strategy: Optional[str] = None
    side: str
    expiration_date: Optional[str] = None
    strike_price: Optional[float] = None
    trade_price: float
    quantity: float
    status: str
    executed_at: str
    synced_at: str
