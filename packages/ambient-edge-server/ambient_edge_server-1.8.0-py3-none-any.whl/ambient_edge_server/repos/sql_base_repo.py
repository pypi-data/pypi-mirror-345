from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ambient_edge_server import config


class SQLBaseRepository:
    def __init__(self):
        self.engine = create_async_engine(
            config.settings.postgres_dsn, future=True, echo=config.settings.sql_debug
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        try:
            async_session = async_sessionmaker(self.engine, class_=AsyncSession)
            async with async_session() as session:
                yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
