import pytest
import pathlib
import os
import docker
import time
import asyncio
from server.configuration.environment import IntegrationTestEnvironment
from server.dependencies.get_environment_cached import get_environment_cached
from server.dependencies.session import get_session
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from server import _init_app
from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from mock import Mock
from fastapi import FastAPI
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import close_all_sessions


@lru_cache
def get_test_environment_cached():
    return IntegrationTestEnvironment()


@lru_cache
def create_test_async_engine():
    environment = get_test_environment_cached()
    return create_async_engine(
        environment.get_db_conn_async(
            db_host=environment.TEST_DB_HOST,
            db_name=environment.TEST_DB_NAME,
            db_port=environment.TEST_DB_PORT,
            db_pass=environment.TEST_DB_PASS,
            db_user=environment.TEST_DB_USER
        ),
        poolclass=NullPool,
        pool_pre_ping=True
    )


def build_test_async_session_maker():
    return sessionmaker(
        create_test_async_engine(),
        expire_on_commit=False,
        class_=AsyncSession
    )


def mock_default_environment_variables():
    return Mock(
        MAIL_TOKEN_SECRET_KEY='secret',
        MAIL_TOKEN_ALGORITHM='HS256',
        MAIL_TOKEN_EXPIRE_DELTA_IN_SECONDS=86400,
        ACCESS_TOKEN_SECRET_KEY="secret",
        ACCESS_TOKEN_ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_DELTA_IN_SECONDS=86400,
        AUTHENTICATOR_DNS="/fake/users/token"
    )


async def get_test_async_session():
    session_maker = build_test_async_session_maker()
    async with session_maker() as session:
        yield session
        await session.close()


@pytest.fixture
async def db_docker_container():

    environment = get_test_environment_cached()

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

    docker_start_sleep_time = 1
    max_retries = 10
    time.sleep(docker_start_sleep_time)
    exec_res = postgres_docker_container.exec_run(
        cmd='pg_isready'
    )

    retries = 0
    while exec_res.exit_code != 0 and retries != max_retries:
        print(retries)
        time.sleep(docker_start_sleep_time)
        exec_res = postgres_docker_container.exec_run(
            cmd='pg_isready'
        )
        print(exec_res.exit_code)
        retries += 1

    try:
        assert retries != max_retries
    except Exception as ex:
        postgres_docker_container.stop()
        raise ex

    return postgres_docker_container


@pytest.fixture
def _test_app(create_db_upgrade, scope="session"):
    app = _init_app()
    app.dependency_overrides[get_session] = get_test_async_session
    return app


@pytest.fixture
def _test_app_default_environment(_test_app: FastAPI) -> FastAPI:
    _test_app.dependency_overrides[get_environment_cached] = mock_default_environment_variables
    return _test_app


@pytest.fixture
def cwd_to_root(scope="session"):
    root_path = pathlib.Path(__file__).parents[3]
    os.chdir(root_path)


@pytest.fixture
async def create_db_upgrade(cwd_to_root, db_docker_container):

    alembic_config = AlembicConfig("alembic.ini")
    try:
        alembic_upgrade(alembic_config, 'head')
    except Exception:
        pass

    yield

    db_docker_container.stop()
    close_all_sessions()
    time.sleep(1)

