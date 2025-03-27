from typing import Any

import fastapi
from sqlalchemy import event
from sqlalchemy.engine import Connection

from config.logger import log
from db.session import engine, SessionLocal
from db.table import Base


# @event.listens_for(target=engine, identifier="connect")
def inspect_db_server_on_connection(
        db_connection: Connection, connection_record: Any
) -> None:
    """
    Log details when a database connection is established.

    :param db_connection: The database connection object
    :param connection_record: Connection record details
    """
    log.info(f"New DB Connection ---\n {db_connection}")
    log.info(f"Connection Record ---\n {connection_record}")


# @event.listens_for(target=engine, identifier="close")
def inspect_db_server_on_close(
        db_connection: Connection, connection_record: Any
) -> None:
    """
    Log details when a database connection is closed.

    :param db_connection: The database connection object
    :param connection_record: Connection record details
    """
    log.info(f"Closing DB Connection ---\n {db_connection}")
    log.info(f"Closed Connection Record ---\n {connection_record}")


def initialize_db_tables() -> None:
    """
    Initialize database tables by dropping and recreating all tables.
    """
    log.info("Database Table Creation --- Initializing . . .")

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    log.info("Database Table Creation --- Successfully Initialized!")


def initialize_db_connection(backend_app: fastapi.FastAPI) -> None:
    """
    Establish database connection and initialize tables.

    :param backend_app: FastAPI application instance
    """
    log.info("Database Connection --- Establishing . . .")

    # Store the engine and session maker in app state
    backend_app.state.db_engine = engine
    backend_app.state.db_session = SessionLocal

    # Initialize tables
    initialize_db_tables()

    log.info("Database Connection --- Successfully Established!")


def dispose_db_connection(backend_app: fastapi.FastAPI) -> None:
    """
    Dispose of the database connection.

    :param backend_app: FastAPI application instance
    """
    log.info("Database Connection --- Disposing . . .")

    backend_app.state.db_engine.dispose()

    log.info("Database Connection --- Successfully Disposed!")
