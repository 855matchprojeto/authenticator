import pytest
import pathlib
import os
import docker
import time
from server.dependencies.get_environment_cached import get_environment_cached
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from server import _init_app
from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient


@lru_cache()
def create_test_async_engine_cached():
    environment = get_environment_cached()
    return create_async_engine(
        environment.get_test_db_conn_async(
            test_db_host=environment.TEST_DB_HOST,
            test_db_name=environment.TEST_DB_NAME,
            test_db_port=environment.TEST_DB_PORT,
            test_db_pass=environment.TEST_DB_PASS,
            test_db_user=environment.TEST_DB_USER
        ),
        echo=environment.DB_ECHO,
        pool_size=environment.DB_POOL_SIZE,
        max_overflow=environment.DB_MAX_OVERFLOW,
        pool_pre_ping=environment.DB_POOL_PRE_PING
    )


def build_test_async_session_maker():
    return sessionmaker(
        create_test_async_engine_cached(),
        expire_on_commit=False,
        class_=AsyncSession
    )


async def get_test_async_session() -> AsyncSession:
    session_maker = build_test_async_session_maker()
    async with session_maker() as session:
        yield session


@pytest.fixture(scope='session')
def db_docker_container():

    environment = get_environment_cached()

    docker_client = docker.from_env()
    postgres_docker_container = docker_client.containers.run(
        image='postgres',
        auto_remove=True,
        detach=True,
        name="db_mc855_authenticator",
        ports={
            "5432/tcp": environment.TEST_DB_PORT
        },
        environment={
            "POSTGRES_PASSWORD": environment.TEST_DB_PASS,
            "POSTGRES_USER": environment.TEST_DB_USER,
            "POSTGRES_DB": environment.TEST_DB_NAME
        }
    )

    time.sleep(1.5)

    return postgres_docker_container


@pytest.fixture(scope='session')
def test_client(create_db_upgrade):
    app = _init_app()
    app.dependency_overrides['get_session'] = get_test_async_session
    return TestClient(app)


@pytest.fixture(scope='session')
def cwd_to_root():
    root_path = pathlib.Path(__file__).parents[3]
    os.chdir(root_path)


@pytest.fixture(scope='session')
def create_db_upgrade(cwd_to_root, db_docker_container):
    environment = get_environment_cached()
    test_database_url = environment.get_test_db_conn_default(
        test_db_host=environment.TEST_DB_HOST,
        test_db_name=environment.TEST_DB_NAME,
        test_db_port=environment.TEST_DB_PORT,
        test_db_pass=environment.TEST_DB_PASS,
        test_db_user=environment.TEST_DB_USER
    )

    alembic_config = AlembicConfig("alembic.ini")

    alembic_config.set_main_option('sqlalchemy.url', test_database_url)
    alembic_upgrade(alembic_config, 'head')

    yield

    db_docker_container.stop()

