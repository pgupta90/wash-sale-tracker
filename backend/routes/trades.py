from fastapi import APIRouter, Query
from typing import Optional, List
from backend.database import search_trades
from backend.config import load_config
from backend.models import Trade

router = APIRouter(prefix='/trades', tags=['trades'])

@router.get('', response_model=List[Trade])
def get_trades(
    symbol: str = Query(..., description="Ticker symbol e.g. META"),
    expiry: Optional[str] = Query(None, description="Expiration date YYYY-MM-DD"),
    strike: Optional[float] = Query(None, description="Strike price"),
):
    config = load_config()
    search_days = config.get('settings', {}).get('search_days', 30)
    return search_trades(symbol=symbol, expiry=expiry, strike=strike, search_days=search_days)
