from fastapi import APIRouter
from backend.auth import get_auth_status
from backend.models import AuthStatus

router = APIRouter(prefix='/auth', tags=['auth'])

@router.get('/status', response_model=AuthStatus)
def auth_status():
    return get_auth_status()
