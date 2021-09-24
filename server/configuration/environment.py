import re
import pathlib
from pydantic import BaseSettings, EmailStr, Field


class Environment(BaseSettings):

    # Configurações do banco de dados

    TEST_DB_HOST = "localhost"
    TEST_DB_USER: str = "postgres"
    TEST_DB_PASS: str = '1234'
    TEST_DB_NAME: str = 'db_mc855_authenticator'
    TEST_DB_PORT: str = '5940'

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

    @staticmethod
    def get_test_db_conn_default(test_db_host: str, test_db_user: str, test_db_pass: str,
                                 test_db_name: str, test_db_port: str):
        return f"postgresql://{test_db_user}:{test_db_pass}@{test_db_host}:{test_db_port}/{test_db_name}"

    @staticmethod
    def get_test_db_conn_async(test_db_host: str, test_db_user: str, test_db_pass: str,
                               test_db_name: str, test_db_port: str):
        return f"postgresql+asyncpg://{test_db_user}:{test_db_pass}@{test_db_host}:{test_db_port}/{test_db_name}"

    class Config:
        env_file = '.env/AUTHENTICATOR.env'
        env_file_encoding = 'utf-8'

