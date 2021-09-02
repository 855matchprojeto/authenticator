from server.configuration.db import AsyncSession, async_db_session


async def get_session() -> AsyncSession:
    async with async_db_session() as session:
        yield session

