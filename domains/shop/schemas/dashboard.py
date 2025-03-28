from typing import Optional

from pydantic import BaseModel


class TotalStockValueAndDailySaleSchema(BaseModel):
    total_purchase_price: Optional[float] = 0.00
    total_sell_price: Optional[float] = 0.00


class SaleSummarySchema(BaseModel):
    monthly_net: Optional[float] = 0.00
    monthly_momo: Optional[float] = 0.00
    monthly_cash: Optional[float] = 0.00
    daily_net: Optional[float] = 0.00
    daily_momo: Optional[float] = 0.00
    daily_cash: Optional[float] = 0.00


class ExpensesSummarySchema(BaseModel):
    monthly_net: Optional[float] = 0.00
    daily_net: Optional[float] = 0.00
