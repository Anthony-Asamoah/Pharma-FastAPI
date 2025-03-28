from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.auth.oauth import get_current_user
from domains.shop.schemas.dashboard import TotalStockValueAndDailySaleSchema
from domains.shop.services.stock import stock_service

dash_router = APIRouter(prefix="/dash")


@dash_router.get(
    "/total_stock_value_and_daily_sale",
    response_model=TotalStockValueAndDailySaleSchema,
)
async def get_total_stock_value_and_daily_sale(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> Any:
    sales = await stock_service.assemble_dash(db=db)
    return sales
