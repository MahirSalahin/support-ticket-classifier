from fastapi import APIRouter, Request
from app.core.limiter import limiter

router = APIRouter()

@router.get("/health", tags=["System"])
@limiter.limit("20/minute")
async def health_check(request: Request):
    return {"status": "ok"}
