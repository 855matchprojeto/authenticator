import pytest
import uuid
from fastapi import FastAPI
from server.tests.integration import db_docker_container, cwd_to_root, create_db_upgrade, _test_client, \
    _test_app, _test_app_default_environment, get_test_async_session
from fastapi.testclient import TestClient
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import SecurityScopes
from server.dependencies.get_security_scopes import get_security_scopes
from server.dependencies.get_email_sender_service import get_email_sender_service
from server.dependencies.get_environment_cached import get_environment_cached
from mock import Mock
from server.tests.integration import build_test_async_session_maker
from server.models.permissao_model import Permissao
from server.models.funcao_model import Funcao
from server.models.vinculo_permissao_funcao_model import VinculoPermissaoFuncao
from server.models.vinculo_usuario_funcao_model import VinculoUsuarioFuncao
from server.models.usuario_model import Usuario
from server.schemas.usuario_schema import UsuarioOutput
from server.tests.integration import get_test_async_session, mock_default_environment_variables
from httpx import AsyncClient
from server.schemas.token_shema import DecodedAccessToken
from server.repository.usuario_repository import UsuarioRepository
from sqlalchemy import and_


def build_mock_email_service():
    mock_email_service = Mock()
    mock_email_service.send_email_background = Mock(
        return_value=None
    )
    return mock_email_service


@pytest.fixture
def _test_app_default_environment_mock_email_service(_test_app_default_environment: FastAPI) -> FastAPI:
    _test_app_default_environment.dependency_overrides[get_email_sender_service] = build_mock_email_service
    return _test_app_default_environment


@pytest.fixture
async def write_default_db_for_get_all_users():
    """
        Permissão "READ_ALL_USERS" e "X"
        Funções F1 (vinculada a READ_ALL_USERS) e F2 (vinculada a X)
        Usuários user1, user2, user3
        user1 ligado a funcao F1, user3 ligado a F1, F2
    """

    session_maker = build_test_async_session_maker()

    async with session_maker() as session:

        # Criando as entidades sem os vinculos

        perm_read_all_users = Permissao(nome='READ_ALL_USERS')
        perm_x = Permissao(nome='x')

        funcao1 = Funcao(nome="F1")
        funcao2 = Funcao(nome="F2")

        user1 = Usuario(
            nome='Teste',
            username='user1',
            email='teste1@unicamp.br',
            hashed_password='secret',
            guid=uuid.uuid4().__str__()
        )

        user2 = Usuario(
            nome='Teste',
            username='user2',
            email='teste2@unicamp.br',
            hashed_password='secret',
            guid=uuid.uuid4().__str__()
        )

        user3 = Usuario(
            nome='Teste',
            username='user3',
            email='teste3@unicamp.br',
            hashed_password='secret',
            guid=uuid.uuid4().__str__()
        )

        session.add_all([
            perm_read_all_users, perm_x, funcao1, funcao2,
            user1, user2, user3]
        )

        await session.flush()

        # Criando vinculos de funcao com permissoes

        session.add(VinculoPermissaoFuncao(
            id_funcao=funcao1.id,
            id_permissao=perm_read_all_users.id
        ))

        session.add(VinculoPermissaoFuncao(
            id_funcao=funcao2.id,
            id_permissao=perm_x.id
        ))

        # Criando vinculos de usuarios com funcoes

        session.add(VinculoUsuarioFuncao(
            id_usuario=user1.id,
            id_funcao=funcao1.id
        ))

        session.add(VinculoUsuarioFuncao(
            id_usuario=user3.id,
            id_funcao=funcao1.id
        ))

        session.add(VinculoUsuarioFuncao(
            id_usuario=user3.id,
            id_funcao=funcao2.id
        ))

        await session.flush()
        await session.commit()
        await session.close()


@pytest.fixture
async def write_single_user_db_nao_verificado():
    """
        Insere um usuário no banco
        hashed_password: HASH da senha 'pass',
    """

    session_maker = build_test_async_session_maker()

    async with session_maker() as session:

        session.add(Usuario(
            nome='Teste',
            username='user',
            email='teste@unicamp.br',
            hashed_password='$2a$12$AgjFKtpe9beYg10zzMNKQeEXaHbz9DF3/0xNRWr4QvJdfPcmq1Rym',
            guid=uuid.uuid4().__str__()
        ))

        await session.flush()
        await session.commit()
        await session.close()


@pytest.fixture
async def write_single_user_db_email_verificado():
    """
        Insere um usuário no banco
        hashed_password: HASH da senha 'pass',
    """

    session_maker = build_test_async_session_maker()

    async with session_maker() as session:

        session.add(Usuario(
            nome='Teste',
            username='user',
            email='teste@unicamp.br',
            hashed_password='$2a$12$AgjFKtpe9beYg10zzMNKQeEXaHbz9DF3/0xNRWr4QvJdfPcmq1Rym',
            guid=uuid.uuid4().__str__(),
            email_verificado=True
        ))

        await session.flush()
        await session.commit()
        await session.close()


class TestUsuarioController:

    """
        Testes dos métodos estáticos de UserService
    """

    """
        Parametros usados no endpoint
        GET ALL USERS
    """

    # username, email, guid, roles, name
    ENOUGH_PERMISSION_READ_ALL_USERS_PARAMETRIZE = [
        ('teste', 'teste@teste.com.br', uuid.uuid4().__str__(), ['1'], 'Teste'),
        ('teste', 'teste@teste.com.br', uuid.uuid4().__str__(), ['1', '2'], 'Teste'),
    ]

    # username, email, guid, roles, name
    NOT_ENOUGH_PERMISSION_READ_ALL_USERS_PARAMETRIZE = [
        ('teste', 'teste@teste.com.br', uuid.uuid4().__str__(), [], 'Teste'),
        ('teste', 'teste@teste.com.br', uuid.uuid4().__str__(), ['2'], 'Teste'),
    ]

    """
        Parametros usados no endpoint
        POST NEW USER
    """

    INVALID_BODY_POST_NEW_USER_PARAMETRIZE = [
        {
            "nome": "User 1", "username": "user1",
            "password": "pass", "email": "test@"  # invalid email
        },
        {
            "nome": "User 2", "username": "user2",
            "password": "pass", "email": "test@.com"  # invalid email
        },
        {
            "nome": "User 3", "username": "user3",
            "password": "pass", "email": "test@.com"  # invalid email
        },
        {
            "nome": "User 3", "username": "user3",
            "email": "test@a.br", "password": "pass"  # invalid email (unicamp)
        }
    ]

    CONFLICT_USER_BODY_POST_NEW_USER_PARAMETRIZE = [
        {
            "nome": "User 1", "username": "user",
            "password": "pass", "email": "a@unicamp.br"  # conflict user
        },
        {
            "nome": "User 1", "username": "a",
            "password": "pass", "email": "teste@unicamp.br"  # conflict email
        }
    ]

    VALID_BODY_POST_NEW_USER_PARAMETRIZE = [
        {
            "nome": "User 1", "username": "user1",
            "password": "pass", "email": "a@unicamp.br"
        }
    ]

    """
        PARAMETROS UTILIZADOS NO ENDPOINT
        LOGIN
    """

    INVALID_FORM_DATA_LOGIN_PARAMETRIZE = [
        {"username": "user"},
        {"password": "pass"}
    ]

    USER_DOES_NOT_EXIST_FORM_DATA_LOGIN_PARAMETRIZE = [
        {"username": "userdoesnotexist", "password": 'pass'}
    ]

    USER_WRONG_PASSWORD_FORM_DATA_LOGIN_PARAMETRIZE = [
        {'username': 'user', 'password': 'wrongpass'}
    ]

    VALID_FORM_DATA_LOGIN_PARAMETRIZE = [
        {'username': 'user', 'password': 'pass'}
    ]

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("username, email, guid, roles, name", ENOUGH_PERMISSION_READ_ALL_USERS_PARAMETRIZE)
    async def test_get_all_users_enough_permissions(
        _test_app_default_environment: FastAPI, username, email,
        guid, roles, name, write_default_db_for_get_all_users
    ):

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

        async with AsyncClient(
                app=_test_app_default_environment,
                base_url='http://test'
        ) as test_async_client:

            test_async_client: AsyncClient

            response = await test_async_client.get(
                'users',
                headers=dict(
                    Authorization=f"Bearer {usr_token}"
                ),
            )

            assert response.status_code == 200
            assert len(response.json()) == 3

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("username, email, guid, roles, name", NOT_ENOUGH_PERMISSION_READ_ALL_USERS_PARAMETRIZE)
    async def test_get_all_users_not_enough_permissions(
        _test_app_default_environment: FastAPI, username, email,
        guid, roles, name, write_default_db_for_get_all_users
    ):

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

        async with AsyncClient(
            app=_test_app_default_environment,
            base_url='http://test'
        ) as test_async_client:

            test_async_client: AsyncClient

            response = await test_async_client.get(
                'users',
                headers=dict(
                    Authorization=f"Bearer {usr_token}"
                ),
            )

            assert response.status_code == 401

    """
        POST NEW USER
    """

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("body", INVALID_BODY_POST_NEW_USER_PARAMETRIZE)
    async def test_post_new_user_invalid_body(
        _test_app_default_environment: FastAPI,
        body
    ):

        async with AsyncClient(
            app=_test_app_default_environment,
            base_url='http://test'
        ) as test_async_client:

            test_async_client: AsyncClient

            response = await test_async_client.post(
                'users',
                json=body
            )

            assert response.status_code == 422

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("body", CONFLICT_USER_BODY_POST_NEW_USER_PARAMETRIZE)
    async def test_post_new_user_conflict_user(
        _test_app_default_environment: FastAPI,
        body, write_single_user_db_nao_verificado
    ):

        async with AsyncClient(
            app=_test_app_default_environment,
            base_url='http://test'
        ) as test_async_client:

            test_async_client: AsyncClient

            response = await test_async_client.post(
                'users',
                json=body
            )

            assert response.status_code == 409

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("body", VALID_BODY_POST_NEW_USER_PARAMETRIZE)
    async def test_post_new_user(
        _test_app_default_environment: FastAPI,
        body, write_single_user_db_nao_verificado
    ):

        async with AsyncClient(
            app=_test_app_default_environment,
            base_url='http://test'
        ) as test_async_client:

            test_async_client: AsyncClient

            response = await test_async_client.post(
                'users',
                json=body
            )

            assert response.status_code == 200

            # Schema validation

            new_user_dict = response.json()
            UsuarioOutput(**new_user_dict)

    """
        LOGIN
    """

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("form_data", INVALID_FORM_DATA_LOGIN_PARAMETRIZE)
    async def test_login_wrong_schema(form_data, _test_app_default_environment):

        async with AsyncClient(
            app=_test_app_default_environment,
            base_url='http://test'
        ) as test_async_client:
            test_async_client: AsyncClient

            response = await test_async_client.post(
                'users/token',
                data=form_data
            )

            assert response.status_code == 422

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("form_data", USER_DOES_NOT_EXIST_FORM_DATA_LOGIN_PARAMETRIZE)
    async def test_login_user_does_not_exist(
        form_data,
        _test_app_default_environment,
        write_single_user_db_nao_verificado
    ):
        async with AsyncClient(
            app=_test_app_default_environment,
            base_url='http://test'
        ) as test_async_client:
            test_async_client: AsyncClient

            response = await test_async_client.post(
                'users/token',
                data=form_data
            )

            assert response.status_code == 403

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("form_data", USER_WRONG_PASSWORD_FORM_DATA_LOGIN_PARAMETRIZE)
    async def test_login_user_wrong_pass(form_data, _test_app_default_environment, write_single_user_db_nao_verificado):
        async with AsyncClient(
            app=_test_app_default_environment,
            base_url='http://test'
        ) as test_async_client:
            test_async_client: AsyncClient

            response = await test_async_client.post(
                'users/token',
                data=form_data
            )

            assert response.status_code == 403

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("form_data", VALID_FORM_DATA_LOGIN_PARAMETRIZE)
    async def test_login_user_not_confirmed_email(form_data, _test_app_default_environment, write_single_user_db_nao_verificado):
        async with AsyncClient(
            app=_test_app_default_environment,
            base_url='http://test'
        ) as test_async_client:
            test_async_client: AsyncClient

            response = await test_async_client.post(
                'users/token',
                data=form_data
            )

            assert response.status_code == 401

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("form_data", VALID_FORM_DATA_LOGIN_PARAMETRIZE)
    async def test_login_user_confirmed_email(
        form_data, _test_app_default_environment,
        write_single_user_db_email_verificado
    ):

        mock_environment = mock_default_environment_variables()

        async with AsyncClient(
            app=_test_app_default_environment,
            base_url='http://test'
        ) as test_async_client:
            test_async_client: AsyncClient

            response = await test_async_client.post(
                'users/token',
                data=form_data
            )

            assert response.status_code == 200

            response_json = response.json()
            assert response_json['token_type'] == 'Bearer'
            assert response_json['expires_in'] == mock_environment.ACCESS_TOKEN_EXPIRE_DELTA_IN_SECONDS

            decoded_token_dict = jwt.decode(
                response_json['access_token'],
                mock_environment.ACCESS_TOKEN_SECRET_KEY,
                algorithms=[mock_environment.ACCESS_TOKEN_ALGORITHM]
            )

            # Validate schema

            decoded_token = DecodedAccessToken(**decoded_token_dict)
            assert decoded_token.username == 'user'

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_email_wrong_schema(
        _test_app_default_environment
    ):

        async with AsyncClient(
            app=_test_app_default_environment,
            base_url='http://test'
        ) as test_async_client:
            test_async_client: AsyncClient

            response = await test_async_client.get(
                'users/verify-email',
                # no params
            )

            assert response.status_code == 422

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_email_wrong_secret_encoding(
        _test_app_default_environment
    ):

        data_to_encode = dict(
            username="user",
            email="teste@dac.unicamp.br",
            name="Teste"
        )

        verify_email_token = jwt.encode(
            data_to_encode,
            'wrong_secret',
            algorithm="HS256"
        )

        async with AsyncClient(
            app=_test_app_default_environment,
            base_url='http://test'
        ) as test_async_client:
            test_async_client: AsyncClient

            response = await test_async_client.get(
                'users/verify-email',
                params=dict(
                    code=verify_email_token
                )
            )

            assert response.status_code == 401

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_email_user_not_found(
        _test_app_default_environment
    ):

        mock_environment = mock_default_environment_variables()

        data_to_encode = dict(
            username="user",
            email="teste@dac.unicamp.br",
            name="Teste"
        )

        verify_email_token = jwt.encode(
            data_to_encode,
            mock_environment.MAIL_TOKEN_SECRET_KEY,
            algorithm=mock_environment.MAIL_TOKEN_ALGORITHM
        )

        async with AsyncClient(
            app=_test_app_default_environment,
            base_url='http://test'
        ) as test_async_client:
            test_async_client: AsyncClient

            response = await test_async_client.get(
                'users/verify-email',
                params=dict(
                    code=verify_email_token
                )
            )

            assert response.status_code == 401

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_email(
        _test_app_default_environment,
        write_single_user_db_nao_verificado
    ):
        mock_environment = mock_default_environment_variables()

        data_to_encode = dict(
            username="user",
            email="teste@unicamp.br",
            name="Teste"
        )

        verify_email_token = jwt.encode(
            data_to_encode,
            mock_environment.MAIL_TOKEN_SECRET_KEY,
            algorithm=mock_environment.MAIL_TOKEN_ALGORITHM
        )

        async with AsyncClient(
            app=_test_app_default_environment,
            base_url='http://test'
        ) as test_async_client:
            test_async_client: AsyncClient

            response = await test_async_client.get(
                'users/verify-email',
                params=dict(
                    code=verify_email_token
                )
            )

            assert response.status_code == 200

            session_maker = build_test_async_session_maker()
            async with session_maker() as _session:
                async with _session.begin():
                    user_repo = UsuarioRepository(_session)
                    users_in_db = await user_repo.find_usuarios_by_filtros([
                        and_(
                            Usuario.email == data_to_encode['email'],
                            Usuario.username == data_to_encode['username']
                        )
                    ])
                    user_in_db = users_in_db[0]
                    assert user_in_db.email_verificado

    @staticmethod
    @pytest.mark.asyncio
    async def test_send_email_verification_link_username_not_found(
        _test_app_default_environment_mock_email_service
    ):

        async with AsyncClient(
            app=_test_app_default_environment_mock_email_service,
            base_url='http://test'
        ) as test_async_client:
            test_async_client: AsyncClient

            response = await test_async_client.post(
                f'users/send-email-verification-link/username_not_in_db',
            )

            assert response.status_code == 404

    @staticmethod
    @pytest.mark.asyncio
    async def test_send_email_verification_link_email_already_confirmed(
        _test_app_default_environment_mock_email_service,
        write_single_user_db_email_verificado
    ):

        async with AsyncClient(
            app=_test_app_default_environment_mock_email_service,
            base_url='http://test'
        ) as test_async_client:
            test_async_client: AsyncClient

            response = await test_async_client.post(
                f'users/send-email-verification-link/user',
            )

            assert response.status_code == 422

    @staticmethod
    @pytest.mark.asyncio
    async def test_send_email_verification_link(
            _test_app_default_environment_mock_email_service,
            write_single_user_db_nao_verificado
    ):
        async with AsyncClient(
            app=_test_app_default_environment_mock_email_service,
            base_url='http://test'
        ) as test_async_client:
            test_async_client: AsyncClient

            response = await test_async_client.post(
                f'users/send-email-verification-link/user',
            )

            assert response.status_code == 204



