from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.auth import router as auth_router
from backend.routes.sync import router as sync_router, _seed
from backend.routes.trades import router as trades_router
from backend.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    _seed()
    yield

app = FastAPI(title='WashSaleCheckerDemo', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f'http://localhost:{p}' for p in range(5173, 5185)],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth_router)
app.include_router(sync_router)
app.include_router(trades_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend.main:app', host='0.0.0.0', port=8001, reload=True)
