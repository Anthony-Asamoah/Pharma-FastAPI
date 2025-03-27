from fastapi import APIRouter

from .expenses import expenses_router
from .receipt import receipt_router
from .sale import sale_router
from .stock import stock_router

shop_router = APIRouter(prefix="/shop")

shop_router.include_router(expenses_router, tags=["EXPENSES"])
shop_router.include_router(receipt_router, tags=["RECEIPTS"])
shop_router.include_router(sale_router, tags=["SALES"])
shop_router.include_router(stock_router, tags=["STOCK"])
