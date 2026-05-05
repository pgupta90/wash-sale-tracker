from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.auth import router as auth_router
from backend.routes.sync import router as sync_router
from backend.routes.trades import router as trades_router
from backend.database import init_db
from backend.auth import login_from_config

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # Fatal if DB unavailable — intentionally unguarded
    try:
        login_from_config()
    except Exception as e:
        print(f"Warning: Could not auto-login on startup: {e}")
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
