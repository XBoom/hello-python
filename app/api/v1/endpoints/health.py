from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DbSession
from app.schemas.common import Response, ok

router = APIRouter(tags=["health"])


@router.get("/health", response_model=Response[dict])
async def health() -> dict:
    return ok({"status": "ok"})


@router.get("/ready", response_model=Response[dict])
async def ready(db: DbSession) -> dict:
    await db.execute(text("SELECT 1"))
    return ok({"status": "ready"})
