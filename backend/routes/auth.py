from fastapi import APIRouter
from backend.auth import get_auth_status
from backend.schwab_auth import get_schwab_status
from backend.models import AuthStatus

router = APIRouter(prefix='/auth', tags=['auth'])

@router.get('/status', response_model=AuthStatus)
def auth_status():
    return get_auth_status()

@router.get('/schwab/status', response_model=AuthStatus)
def schwab_auth_status():
    return get_schwab_status()
