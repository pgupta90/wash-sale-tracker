from fastapi import APIRouter
from backend.database import get_last_synced, set_last_synced, upsert_trade
from backend.models import SyncStatus
from backend.demo_data import DEMO_TRADES
from datetime import datetime, timezone

router = APIRouter(prefix='/sync', tags=['sync'])

_sync_state: dict = {'status': 'idle', 'error': None}


def _seed():
    now = datetime.now(timezone.utc).isoformat()
    for trade in DEMO_TRADES:
        upsert_trade({**trade, 'synced_at': now})
    set_last_synced(now)


@router.get('/status', response_model=SyncStatus)
def sync_status():
    return SyncStatus(
        status=_sync_state['status'],
        last_synced=get_last_synced(),
        error=_sync_state['error'],
    )


@router.post('', response_model=SyncStatus)
def trigger_sync():
    _sync_state['status'] = 'syncing'
    _sync_state['error'] = None
    try:
        _seed()
        _sync_state['status'] = 'idle'
    except Exception as e:
        _sync_state['status'] = 'error'
        _sync_state['error'] = str(e)
    return SyncStatus(
        status=_sync_state['status'],
        last_synced=get_last_synced(),
        error=_sync_state['error'],
    )
