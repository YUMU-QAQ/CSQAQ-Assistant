"""FastAPI application entry point."""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .services.cache_service import cache

# Import all routers
from .routers import (
    market,
    items,
    rankings,
    watchlist,
    portfolio,
    alerts,
    arbitrage,
    cases,
    ai,
    feishu,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Startup
    await init_db()
    asyncio.create_task(cache.cleanup_expired())
    # Start alert checker for Feishu push (every 120 seconds)
    asyncio.create_task(alert_check_loop())
    yield
    # Shutdown
    from .services.csqaq_client import csqaq_client
    await csqaq_client.close()


async def alert_check_loop():
    """Background task: check alerts and push to Feishu."""
    from .database import async_session
    from .services.feishu_service import feishu_pusher
    await asyncio.sleep(30)  # Wait for startup
    while True:
        try:
            async with async_session() as db:
                await feishu_pusher.check_and_push_alerts(db)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Alert check error: {e}")
        await asyncio.sleep(120)  # Every 2 minutes


app = FastAPI(
    title="CSQAQ Assistant API",
    description="CS2 Skin Data Analysis Assistant — Backend API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend (dev + production)
cors_origins = [settings.frontend_origin]
# Always allow localhost dev servers
cors_origins += [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]
# Deduplicate
cors_origins = list(dict.fromkeys(cors_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(market.router)
app.include_router(items.router)
app.include_router(rankings.router)
app.include_router(watchlist.router)
app.include_router(portfolio.router)
app.include_router(alerts.router)
app.include_router(arbitrage.router)
app.include_router(cases.router)
app.include_router(ai.router)
app.include_router(feishu.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "CSQAQ Assistant API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
