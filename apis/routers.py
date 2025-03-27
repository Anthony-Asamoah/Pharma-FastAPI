from fastapi import APIRouter

from apis.health import health_router
from domains.auth.apis import auth_routers
from domains.shop.apis import shop_router

router = APIRouter()
router.include_router(router=health_router)
router.include_router(router=auth_routers)
router.include_router(router=shop_router)
