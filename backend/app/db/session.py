# backend/app/db/session.py
import sqlalchemy.ext.asyncio as sa_async
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

engine = sa_async.create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_size=20,
    max_overflow=10,
    echo=False,
)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=sa_async.AsyncSession, expire_on_commit=False
)

Base = declarative_base()


# Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
