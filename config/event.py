from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.logger import log
# from db.events import inspect_db_server_on_connection, inspect_db_server_on_close  # noqa
from utils.create_superuser import create_system_admin


@asynccontextmanager
async def event_manager(app: FastAPI):
    log.info(msg=f"Initializing {app.title}")
    await create_system_admin()
    log.info(msg=f"Application v{app.version} started elegantly!")
    yield
    log.info(msg="Goodbye 🚀")

    log.info(msg=f"Application v{app.version} shut down gracefully!")
