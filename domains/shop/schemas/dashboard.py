from pydantic import BaseModel


class TotalStockValueAndDailySaleSchema(BaseModel):
    total_purchase_price: float
    total_sell_price: float


class SaleSummarySchema(BaseModel):
    monthly_net: float
    monthly_momo: float
    monthly_cash: float
    daily_net: float
    daily_momo: float
    daily_cash: float
