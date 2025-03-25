from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import settings

# Create async engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.IS_DB_ECHO_LOG,
    pool_size=settings.DB_POOL_SIZE,
    pool_recycle=3600,
    max_overflow=settings.DB_POOL_OVERFLOW,
    pool_pre_ping=True,
)

# Create async session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
