from typing import Optional, List

from pydantic import BaseModel

from domains.shop.schemas.stock import VanillaStockSchema


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


class StockSummarySchema(BaseModel):
    most_issued: List[VanillaStockSchema]
    most_profitable: List[VanillaStockSchema]
    most_refunded: List[VanillaStockSchema]
    soon_expiring: List[VanillaStockSchema]
    gross_stock_value: float
    raw_expected_return: Optional[float]
