from fastapi import APIRouter
from backend.models import AuthStatus

router = APIRouter(prefix='/auth', tags=['auth'])

@router.get('/status', response_model=AuthStatus)
def auth_status():
    return AuthStatus(authenticated=True, error=None)
