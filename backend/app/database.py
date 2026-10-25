from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

Base = declarative_base()


def ensure_database() -> None:
    """Create the target database if it does not exist yet."""
    engine = create_engine(settings.server_database_uri, pool_pre_ping=True)
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{settings.MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        conn.commit()
    engine.dispose()


def create_engine_with_db() -> object:
    return create_engine(
        settings.database_uri,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


engine = create_engine_with_db()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    ensure_database()
    # Import models so they are registered on Base metadata.
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
