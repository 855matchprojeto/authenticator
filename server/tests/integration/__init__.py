import pytest
import pathlib
import os
import docker
import time
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
from server.models.funcao_model import Funcao
from server.models.permissao_model import Permissao
from server.models.vinculo_permissao_funcao_model import VinculoPermissaoFuncao


@lru_cache
def get_test_environment_cached():
    return IntegrationTestEnvironment()


def create_test_async_engine_cached():
    environment = get_test_environment_cached()
    return create_async_engine(
        environment.get_db_conn_async(
            db_host=environment.TEST_DB_HOST,
            db_name=environment.TEST_DB_NAME,
            db_port=environment.TEST_DB_PORT,
            db_pass=environment.TEST_DB_PASS,
            db_user=environment.TEST_DB_USER
        ),
    )


def build_test_async_session_maker():
    return sessionmaker(
        create_test_async_engine_cached(),
        expire_on_commit=False,
        class_=AsyncSession
    )


def mock_default_environment_variables():
    return Mock(
        ACCESS_TOKEN_SECRET_KEY="secret",
        ACCESS_TOKEN_ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_DELTA_IN_SECONDS=86400,
        MAIL_TOKEN_SECRET_KEY="secret",
        MAIL_TOKEN_ALGORITHM="HS256",
        MAIL_TOKEN_EXPIRE_DELTA_IN_SECONDS=86400,
        SERVER_DNS="SERVER_DNS"
    )


async def get_test_async_session():
    session_maker = build_test_async_session_maker()
    async with session_maker() as session:
        yield session


@pytest.fixture()
def db_docker_container():

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

    time.sleep(1.5)

    return postgres_docker_container


@pytest.fixture()
def _test_app(create_db_upgrade):
    app = _init_app()
    app.dependency_overrides[get_session] = get_test_async_session
    return app


@pytest.fixture()
def _test_client(_test_app):
    return TestClient(_test_app)


@pytest.fixture()
def _test_app_default_environment(_test_app: FastAPI) -> FastAPI:
    _test_app.dependency_overrides[get_environment_cached] = mock_default_environment_variables
    return _test_app


@pytest.fixture()
def cwd_to_root():
    root_path = pathlib.Path(__file__).parents[3]
    os.chdir(root_path)


@pytest.fixture()
async def create_db_upgrade(cwd_to_root, db_docker_container):

    environment = get_test_environment_cached()

    alembic_config = AlembicConfig("alembic.ini")
    alembic_upgrade(alembic_config, 'head')

    try:
        await write_permissions_db()
    except Exception as ex:
        db_docker_container.stop()
        raise ex

    yield

    db_docker_container.stop()

    time.sleep(1)


async def write_permissions_db():
    """
        Criando permissões e funções MOCK para o banco de dados
        (F1 -> P1, P2, P3)
        (F2 -> P4)
        (F3 -> )
    """

    session_maker = build_test_async_session_maker()

    async with session_maker() as session:

        # Criando função F1 -> Ligada a várias permissoes (P1, P2, P3)

        funcao1 = Funcao(nome="F1")
        perm1 = Permissao(nome='P1')
        perm2 = Permissao(nome='P2')
        perm3 = Permissao(nome='P3')

        session.add_all([funcao1, perm1, perm2, perm3])
        await session.flush()

        for perm in [perm1, perm2, perm3]:
            session.add(
                VinculoPermissaoFuncao(
                    id_funcao=funcao1.id,
                    id_permissao=perm.id
                )
            )

        await session.flush()

        # Criando função F2 -> Ligada apenas a uma permissao P4

        funcao2 = Funcao(nome="F2")
        perm4 = Permissao(nome='P4')
        session.add_all([funcao2, perm4])
        await session.flush()

        session.add(
            VinculoPermissaoFuncao(
                id_funcao=funcao2.id,
                id_permissao=perm4.id
            )
        )

        # Criando função F3 -> Não está ligada a nenhuma permissão

        session.add(
            Funcao(nome="F3")
        )

        await session.flush()
        await session.commit()
        await session.close()
