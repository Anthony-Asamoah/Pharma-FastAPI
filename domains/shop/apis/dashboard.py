from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.auth.oauth import get_current_user
from domains.shop.schemas.dashboard import TotalStockValueAndDailySaleSchema, SaleSummarySchema
from domains.shop.services.expenses import expenses_service
from domains.shop.services.sale import sale_service
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


@dash_router.get(
    "/summaries/sales",
    response_model=SaleSummarySchema,
)
async def get_sale_summary(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> Any:
    sales = await sale_service.assemble_dash(db=db)
    return sales


@dash_router.get(
    "/summaries/expenses",
    response_model=SaleSummarySchema,
)
async def get_expenses_summary(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> Any:
    sales = await expenses_service.assemble_dash(db=db)
    return sales
