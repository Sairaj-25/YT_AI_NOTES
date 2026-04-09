from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from pathlib import Path
from sqlalchemy.orm import declarative_base
from core.config import get_settings
from typing import AsyncGenerator

settings = get_settings()

BASE_DIR = Path(__file__).resolve().parent.parent

SQLALCHEMY_DATABASE_URL = (
    settings.DATABASE_URL
)

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession() as Session:
        try:
            yield Session
        finally:
            await Session.close()