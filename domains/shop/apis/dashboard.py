from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.auth.oauth import get_current_user
from domains.shop.schemas.dashboard import TotalStockValueAndDailySaleSchema, SaleSummarySchema, StockSummarySchema
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
    sales = await stock_service.get_total_stock_value_and_daily_sale(db=db)
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


@dash_router.get(
    "/summaries/stock",
    response_model=StockSummarySchema,
)
async def get_stock_summary(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 5,
        time_range_from: datetime = None,
        time_range_to: datetime = None,
) -> Any:
    sales = await stock_service.assemble_summary(
        db=db, skip=skip, limit=limit,
        time_range_min=time_range_from, time_range_max=time_range_to,
    )
    return sales
