from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.config import settings
from models.base import Base
from models import user, chat

engine = create_async_engine(settings.database_url, echo=settings.DEBUG)

session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with session_factory() as session:
        yield session
