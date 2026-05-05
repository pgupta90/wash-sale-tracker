from fastapi import APIRouter
from backend.sync import sync_stock_orders, sync_option_orders
from backend.database import get_last_synced, set_last_synced
from backend.models import SyncStatus
from datetime import datetime, timezone

router = APIRouter(prefix='/sync', tags=['sync'])

_sync_state: dict = {'status': 'idle', 'error': None}

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
        sync_stock_orders()
        sync_option_orders()
        set_last_synced(datetime.now(timezone.utc).isoformat())
        _sync_state['status'] = 'idle'
    except Exception as e:
        _sync_state['status'] = 'error'
        _sync_state['error'] = str(e)
    return SyncStatus(
        status=_sync_state['status'],
        last_synced=get_last_synced(),
        error=_sync_state['error'],
    )
