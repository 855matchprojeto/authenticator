import re
from pydantic import BaseSettings, EmailStr


class Environment(BaseSettings):

    # Configurações do banco de dados

    DB_HOST: str = "localhost"
    DB_USER: str = 'postgres'
    DB_PASS: str = '1234'
    DB_NAME: str = 'db_mc855_authenticator'
    DB_PORT: str = '5438'
    DB_ECHO: bool = True
    DB_POOL_SIZE: int = 80
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_PRE_PING: bool = True

    DATABASE_URL: str

    # Configurações do servidor

    ENVIRONMENT: str = 'DEV'
    HOST: str = 'localhost'
    PORT: int = 8080

    ACCESS_TOKEN_EXPIRE_DELTA_IN_SECONDS: int = 1800
    MAIL_TOKEN_EXPIRE_DELTA_IN_SECONDS: int = 600

    ACCESS_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_ALGORITHM: str

    MAIL_TOKEN_SECRET_KEY: str
    MAIL_TOKEN_ALGORITHM: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_TLS: int
    MAIL_SSL: int
    MAIL_USE_CREDENTIALS: int

    SERVER_DNS: str

    @staticmethod
    def get_db_conn_async(database_url: str):
        return re.sub(r'\bpostgres://\b', "postgresql+asyncpg://", database_url, count=1)

    @staticmethod
    def get_db_conn_default(database_url: str):
        return re.sub(r'\bpostgres://\b', "postgresql://", database_url, count=1)

    class Config:
        env_file = '.env/AUTHENTICATOR.env'
        env_file_encoding = 'utf-8'

