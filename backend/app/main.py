from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.notes import router as notes_router
from app.database import get_pool, close_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: warm the DB pool so first request isn't slow
    await get_pool()
    yield
    # Shutdown: close cleanly
    await close_pool()


app = FastAPI(title="Notes API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notes_router, prefix="/notes", tags=["notes"])


@app.get("/health")
async def health_check():
    """
    Deep health check — verifies DB + cache are reachable.
    Docker uses this endpoint for the container health status.
    """
    from app.database import get_pool
    from app.cache import get_redis
    checks = {}

    try:
        pool = await get_pool()
        await pool.fetchval("SELECT 1")
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = f"error: {e}"

    try:
        redis = get_redis()
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"

    all_ok = all(v == "ok" for v in checks.values())
    return {"status": "ok" if all_ok else "degraded", "checks": checks}