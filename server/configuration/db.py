from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from server.configuration import environment

Base = declarative_base()

engine = create_async_engine(
    environment.DB_CONN_ASYNC,
    echo=environment.DB_ECHO,
    pool_size=environment.DB_POOL_SIZE,
    max_overflow=environment.DB_MAX_OVERFLOW,
    pool_pre_ping=environment.DB_POOL_PRE_PING
)

async_db_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

