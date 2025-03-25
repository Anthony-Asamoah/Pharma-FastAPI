from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.session import get_db

health_router = APIRouter(tags=["API HEALTH CHECKER"])


@health_router.get(
    path="/health",
    response_class=JSONResponse,
    status_code=status.HTTP_200_OK,
)
async def check_health(db: Session = Depends(get_db)) -> JSONResponse:
    return JSONResponse(content={"status": "healthy"})
