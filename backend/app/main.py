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
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Startup
    await init_db()
    asyncio.create_task(cache.cleanup_expired())
    yield
    # Shutdown
    from .services.csqaq_client import csqaq_client
    await csqaq_client.close()


app = FastAPI(
    title="CSQAQ Assistant API",
    description="CS2 Skin Data Analysis Assistant — Backend API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
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
