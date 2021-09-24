import pytest
import uuid
from fastapi import FastAPI
from server.tests.integration import db_docker_container, cwd_to_root, create_db_upgrade, _test_client, \
    _test_app, _test_app_default_environment, get_test_async_session, write_permissions_db
from fastapi.testclient import TestClient
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import SecurityScopes
from server.dependencies.get_security_scopes import get_security_scopes
from mock import Mock


def all_perms():
    perms = ['P1', 'P2', 'P3', 'P4']
    return Mock(
        scopes=perms,
        scope_str=",".join(perms)
    )


@pytest.fixture
def current_user_token_valid():

    data_to_encode = {
        "username": "user",
        "email": "teste@teste.com",
        "guid": uuid.uuid4().__str__(),
        "roles": [1],
        "name": "Teste"
    }

    return jwt.encode(
        data_to_encode,
        "secret",
        algorithm="HS256"
    )


@pytest.fixture
def current_user_token_wrong_secret():

    data_to_encode = {
        "username": "user",
        "email": "teste@teste.com",
        "guid": uuid.uuid4().__str__(),
        "roles": [1],
        "name": "Teste"
    }

    return jwt.encode(
        data_to_encode,
        "wrong",
        algorithm="HS256"
    )


@pytest.fixture
def current_user_token_expired():

    timestamp_atual = datetime.utcnow()
    timestamp_exp = timestamp_atual - timedelta(seconds=1)

    data_to_encode = {
        "username": "user",
        "email": "teste@teste.com",
        "guid": uuid.uuid4().__str__(),
        "roles": [1],
        "name": "Teste",
        "exp": timestamp_exp
    }

    return jwt.encode(
        data_to_encode,
        "wrong",
        algorithm="HS256"
    )


@pytest.fixture
def current_user_wrong_schema():

    data_to_encode = {
        "username": "user",
        "email": "teste@teste.com",
        "guid": uuid.uuid4().__str__(),
        "roles": [1],
        "nome": "Teste",  # "nome" ao inves de "name"
    }

    return jwt.encode(
        data_to_encode,
        "wrong",
        algorithm="HS256"
    )


class TestUsuarioService:

    """
        Testes dos métodos estáticos de UserService
    """

    # username, email, guid, roles, name, security_scopes_overrider
    ENOUGH_PERMISSION_DATA = [
        ('teste', 'teste@teste.com.br', uuid.uuid4().__str__(), ['1', '2', '3'], 'Teste', all_perms),
        ('teste', 'teste@teste.com.br', uuid.uuid4().__str__(), ['1', '2'], 'Teste', all_perms),
    ]

    @staticmethod
    @pytest.mark.asyncio
    def test_get_current_user_no_headers(_test_app_default_environment: FastAPI, _test_client: TestClient):

        response = _test_client.get(
            'users',
        )
        assert response.status_code == 401

    @staticmethod
    @pytest.mark.asyncio
    def test_get_current_user_wrong_secret(_test_app_default_environment: FastAPI, _test_client: TestClient,
                                           current_user_token_wrong_secret):

        response = _test_client.get(
            'users',
            headers=dict(
                Authorization=f"Bearer {current_user_token_wrong_secret}"
            ),
        )
        # assert response.status_code == 401

    @staticmethod
    @pytest.mark.asyncio
    def test_get_current_user_expired_token(_test_app_default_environment: FastAPI, _test_client: TestClient,
                                            current_user_token_expired):

        response = _test_client.get(
            'users',
            headers=dict(
                Authorization=f"Bearer {current_user_token_expired}"
            ),
        )
        # assert response.status_code == 401

    @staticmethod
    @pytest.mark.asyncio
    def test_get_current_user_wrong_schema_validation(
        _test_app_default_environment: FastAPI, _test_client: TestClient,
        current_user_wrong_schema
    ):

        response = _test_client.get(
            'users',
            headers=dict(
                Authorization=f"Bearer {current_user_wrong_schema}"
            ),
        )
        assert response.status_code == 401

    @staticmethod
    @pytest.mark.parametrize("username, email, guid, roles, name, security_scopes_overrider",
                             ENOUGH_PERMISSION_DATA)
    def test_current_user_enough_permissions(
            _test_app_default_environment: FastAPI, _test_client: TestClient,
            username, email, guid, roles, security_scopes_overrider,
            name
    ):
        _test_app_default_environment.dependency_overrides[get_security_scopes] = security_scopes_overrider

        data_to_encode = dict(
            username=username,
            email=email,
            guid=guid,
            roles=roles,
            name=name
        )

        usr_token = jwt.encode(
            data_to_encode,
            'secret',
            algorithm="HS256"
        )

        response = _test_client.get(
            'users',
            headers=dict(
                Authorization=f"Bearer {usr_token}"
            ),
        )

        assert response.status_code == 200

