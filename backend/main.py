from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.auth import router as auth_router
from backend.routes.sync import router as sync_router
from backend.routes.trades import router as trades_router
from backend.database import init_db
from backend.auth import login_from_config
from backend.schwab_auth import get_schwab_status

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # Fatal if DB unavailable — intentionally unguarded
    # Login using saved session from ~/.tokens/robinhood.pickle (set up by backend/authenticate.py)
    result = login_from_config()
    if not result.get('authenticated'):
        print()
        print("WARNING: Not authenticated with Robinhood.")
        print("Run this once to set up your session:")
        print("  python3 backend/authenticate.py")
        print()
    schwab_result = get_schwab_status()
    if not schwab_result.get('authenticated'):
        print()
        print("WARNING: Not authenticated with Schwab.")
        print("Run this once to set up your session:")
        print("  python3.11 backend/schwab_authenticate.py")
        print()
    yield

app = FastAPI(title='WashSaleApp', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth_router)
app.include_router(sync_router)
app.include_router(trades_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend.main:app', host='0.0.0.0', port=8000, reload=True)
