from typing import Any

from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_400_BAD_REQUEST
from uvicorn import run

from apis.routers import router
from config.event import event_manager
from config.settings import AppSettings, settings
from utils.exceptions.exc_500 import http_500_exc_internal_server_error


class App:
    def __init__(self, event_manager: Any, router: APIRouter, settings: AppSettings):
        self.__app = FastAPI(lifespan=event_manager, **settings.set_app_attributes)  # type: ignore
        self.__setup_middlewares(settings=settings)
        self.__add_routes(router=router, settings=settings)

    def __setup_middlewares(self, settings: AppSettings):
        self.__app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.ALLOWED_ORIGIN_LIST,
            allow_credentials=settings.IS_ALLOWED_CREDENTIALS,
            allow_methods=settings.ALLOWED_METHOD_LIST,
            allow_headers=settings.ALLOWED_HEADER_LIST,
        )

    def __add_routes(self, router: APIRouter, settings: AppSettings):
        self.__app.include_router(router=router, prefix=settings.API_PREFIX)

    def __call__(self) -> FastAPI:
        return self.__app


def initialize_application() -> FastAPI:
    return App(event_manager=event_manager, router=router, settings=settings)()


app = initialize_application()


@app.exception_handler(ValueError)
async def generic_exception_handler(request: Request, exc: Exception):
    raise HTTPException(
        status_code=HTTP_400_BAD_REQUEST,
        detail=str(exc),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    raise await http_500_exc_internal_server_error()


if __name__ == "__main__":
    run(
        app="main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=False,
        workers=settings.SERVER_WORKERS,
    )
