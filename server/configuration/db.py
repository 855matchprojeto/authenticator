from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from server.configuration import environment

Base = declarative_base()


engine = create_async_engine(
    'postgresql+asyncpg://xojmqlwdxfynpb:8a0a8cc1689c0e066ac33dc6fca194bf610cc764d6f71c87e6318dd49c82fa52@ec2-18-209-153-180.compute-1.amazonaws.com:5432/dcbi94kke45ffj',
    echo=environment.DB_ECHO,
    pool_size=environment.DB_POOL_SIZE,
    max_overflow=environment.DB_MAX_OVERFLOW,
    pool_pre_ping=environment.DB_POOL_PRE_PING
)

async_db_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

