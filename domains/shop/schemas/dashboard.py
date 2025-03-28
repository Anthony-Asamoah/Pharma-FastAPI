from pydantic import BaseModel


class TotalStockValueAndDailySaleSchema(BaseModel):
    total_purchase_price: float
    total_sell_price: float
