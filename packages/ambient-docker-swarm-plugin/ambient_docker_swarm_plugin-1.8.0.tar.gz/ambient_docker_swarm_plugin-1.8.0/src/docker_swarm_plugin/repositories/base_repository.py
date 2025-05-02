from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class SQLBaseRepository:
    def __init__(self):
        self.engine = create_async_engine(
            "sqlite+aiosqlite:////var/lib/ambient_edge_server\
/plugins/docker_swarm_plugin/docker_swarm.db",
            future=True,
            echo=False,
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
