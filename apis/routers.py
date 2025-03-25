from fastapi import APIRouter

from apis.health import health_router
from domains.auth.apis import auth_routers

router = APIRouter()
router.include_router(router=health_router)
router.include_router(router=auth_routers)
