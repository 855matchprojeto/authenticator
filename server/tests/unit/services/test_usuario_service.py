import uuid

import pytest
import time
from server.services.usuario_service import UsuarioService
from datetime import timedelta
from jose import jwt, JWTError
from mock import Mock, AsyncMock
from server.configuration import exceptions

"""
    Fixtures
"""


@pytest.fixture
def user_keys_to_check_in_access_token():
    return ["guid", "name", "email", "username", "roles"]


@pytest.fixture
def expected_token_type():
    return "Bearer"


@pytest.fixture
def empty_arr():
    return []


@pytest.fixture
def single_user_arr_email_nao_verificado():
    """
        Retorna um usuário com um hash da senha "pass" e email nao verificado
    """
    return [
        Mock(
            id=1,
            username="user",
            email="teste@unicamp.br",
            email_verificado=False,
            hashed_password="$2a$12$AgjFKtpe9beYg10zzMNKQeEXaHbz9DF3/0xNRWr4QvJdfPcmq1Rym",
            guid=uuid.uuid4(),
            nome="Teste",
            vinculos_usuario_funcao=[
                Mock(
                    id_usuario=1,
                    id_funcao=1,
                )
            ]
        )
    ]


@pytest.fixture
def single_user_arr_email_verificado():
    """
        Retorna um usuário com um hash da senha "pass" e email_verificado
    """
    return [
        Mock(
            username="user",
            email="teste@unicamp.br",
            email_verificado=True,
            hashed_password="$2a$12$AgjFKtpe9beYg10zzMNKQeEXaHbz9DF3/0xNRWr4QvJdfPcmq1Rym",
            guid=uuid.uuid4(),
            nome="Teste",
            vinculos_usuario_funcao=[
                Mock(
                    id_usuario=1,
                    id_funcao=1,
                )
            ]
        )
    ]


class TestUsuarioService:

    """
        Funções auxiliares
    """

    @staticmethod
    def assert_validate_token(data_before_encode: dict, token: str, secret_key: str, algorithm: str, expires_in: int):
        decoded_token = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm]
        )

        # Verifica que os dados antes de serem codificados
        # são um subconjunto do token decodificado
        assert data_before_encode.items() <= decoded_token.items()

        # Verifica se os campos 'iat' e 'exp' pertencem ao token
        assert "iat" in decoded_token.keys() and "exp" in decoded_token.keys()

        # Verifica se a diferença entre exp e iat é de expires_in
        assert (decoded_token["exp"] - decoded_token["iat"]) == expires_in

    """
        Testes dos métodos estáticos de UserService
    """

    @staticmethod
    @pytest.mark.parametrize("pwd", [
        "Hv=]hamXd9Sj:+td",
        "a",
        "b",
        "senha",
        "123",
        "$JkHEFujp@9GG-%m",
        "H_2nJ?ck2e^_*RBE"
    ])
    def test_criptografa_verifica_senha_correta(pwd):
        senha_criptografada = UsuarioService.criptografa_senha(pwd)
        assert UsuarioService.verifica_senha(pwd, senha_criptografada) is True

    @staticmethod
    @pytest.mark.parametrize("pwd, pwd_to_compare", [
        ("Hv=]hamXd9Sj:+td", "Hv=]hamXd9Sj:+td1"),
        ("a", "b"),
        ("b", "a"),
        ("senha", "senha123"),
        ("123", "1234"),
        ("$JkHEFujp@9GG-%m", "a"),
        ("H_2nJ?ck2e^_*RBE", "123")
    ])
    def test_criptografa_verifica_senha_incorreta(pwd, pwd_to_compare):
        senha_criptografada = UsuarioService.criptografa_senha(pwd)
        assert UsuarioService.verifica_senha(pwd_to_compare, senha_criptografada) is False

    @staticmethod
    @pytest.mark.parametrize("data_to_encode, secret_key, algorithm, expires_in", [
        ({"key": "value"}, "secret", "HS256", 3600),
        ({"key": "value"}, "secret2", "HS512", 2),
    ])
    def test_gera_token_validacao_correta(data_to_encode, secret_key, algorithm, expires_in):

        # Gera o token
        expires_delta = timedelta(seconds=expires_in)
        token = UsuarioService.gera_token(
            data_to_encode,
            expires_delta,
            secret_key,
            algorithm,
        )

        # Decodifica e valida o token
        TestUsuarioService.assert_validate_token(
            data_to_encode,
            token,
            secret_key,
            algorithm,
            expires_in
        )

    @staticmethod
    @pytest.mark.parametrize("data_to_encode, secret_key, algorithm, expires_in, wrong_secret_key", [
        ({"key": "value"}, "secret", "HS256", 3600, "wrong"),
        ({"key": "value"}, "secret2", "HS512", 2, "wrong"),
    ])
    def test_gera_token_secret_key_incorreta(data_to_encode, secret_key, algorithm, expires_in, wrong_secret_key):

        # Gera o token
        expires_delta = timedelta(seconds=expires_in)
        token = UsuarioService.gera_token(
            data_to_encode,
            expires_delta,
            secret_key,
            algorithm,
        )

        with pytest.raises(JWTError):
            # Decodifica o token
            decoded_token = jwt.decode(
                token,
                wrong_secret_key,
                algorithms=[algorithm]
            )

    @staticmethod
    @pytest.mark.parametrize("data_to_encode, secret_key, algorithm, expires_in", [
        ({"key": "value"}, "secret", "HS256", -1),
        ({"key": "value"}, "secret2", "HS512", -3),
        ({"key": "value"}, "secret2", "HS512", 1)
    ])
    def test_gera_token_expired_token(data_to_encode, secret_key, algorithm, expires_in):

        # Gera o token
        expires_delta = timedelta(seconds=expires_in)
        token = UsuarioService.gera_token(
            data_to_encode,
            expires_delta,
            secret_key,
            algorithm,
        )

        if expires_in > 0:
            time.sleep(expires_in + 1)

        with pytest.raises(JWTError):
            # Decodifica o token
            decoded_token = jwt.decode(
                token,
                secret_key,
                algorithms=[algorithm]
            )

    """
        Testes dos serviços chamados pelos controllers
    """

    @staticmethod
    @pytest.mark.asyncio
    async def test_gera_novo_token_login_username_does_not_exist(empty_arr):

        """
            O repository retorna um array vazio mockado, simbolizando que
            o usuário não foi encontrado!
        """

        form_data_mock = Mock()
        form_data_mock.username = "user"
        form_data_mock.password = "pass"

        user_repo_mock = Mock()
        user_repo_mock.find_usuarios_by_filtros = AsyncMock(return_value=empty_arr)

        service = UsuarioService(
            user_repo=user_repo_mock
        )

        with pytest.raises(exceptions.InvalidUsernamePasswordException):
            await service.gera_novo_token_login(form_data_mock)

    @staticmethod
    @pytest.mark.asyncio
    async def test_gera_novo_token_login_invalid_password(single_user_arr_email_verificado):
        """
            O repository retorna um array unitário mockado.
            O usuário retornado tem o hash da senha "pass".
            Será enviada uma senha errada de propósito e é
            esperado que seja retornada uma exceção
        """

        form_data_mock = Mock()
        form_data_mock.username = "user"
        form_data_mock.password = "wrong_pass"

        user_repo_mock = Mock()
        user_repo_mock.find_usuarios_by_filtros = AsyncMock(return_value=single_user_arr_email_verificado)

        service = UsuarioService(
            user_repo=user_repo_mock
        )

        with pytest.raises(exceptions.InvalidUsernamePasswordException):
            await service.gera_novo_token_login(form_data_mock)

    @staticmethod
    @pytest.mark.asyncio
    async def test_gera_novo_token_login_email_nao_confirmado(single_user_arr_email_nao_verificado):
        """
            O repository retorna um array unitário mockado.
            O usuário retornado tem o hash da senha "pass".
            Será enviada uma senha errada de propósito e é
            esperado que seja retornada uma exceção
        """

        form_data_mock = Mock()
        form_data_mock.username = "user"
        form_data_mock.password = "pass"

        user_repo_mock = Mock()
        user_repo_mock.find_usuarios_by_filtros = AsyncMock(return_value=single_user_arr_email_nao_verificado)

        service = UsuarioService(
            user_repo=user_repo_mock
        )

        with pytest.raises(exceptions.InvalidEmailException):
            await service.gera_novo_token_login(form_data_mock)

    @staticmethod
    @pytest.mark.parametrize("secret, expires_in", [
        ("secret", 3600),
        ("secret2", 1800),
    ])
    @pytest.mark.asyncio
    async def test_gera_novo_token_login_usuario_valido(
            single_user_arr_email_verificado, user_keys_to_check_in_access_token,
            expected_token_type, secret, expires_in):
        """
            O repository retorna um array unitário mockado.
            O usuário retornado tem o hash da senha "pass".
            Será enviada uma senha errada de propósito e é
            esperado que seja retornada uma exceção
        """

        user = single_user_arr_email_verificado[0]

        form_data_mock = Mock()
        form_data_mock.username = "user"
        form_data_mock.password = "pass"

        user_repo_mock = Mock()
        user_repo_mock.find_usuarios_by_filtros = AsyncMock(return_value=single_user_arr_email_verificado)

        environment_mock = Mock(
            ACCESS_TOKEN_EXPIRE_DELTA_IN_SECONDS=expires_in,
            ACCESS_TOKEN_SECRET_KEY=secret,
            ACCESS_TOKEN_ALGORITHM="HS256"
        )

        service = UsuarioService(
            user_repo=user_repo_mock,
            environment=environment_mock
        )

        response_json = await service.gera_novo_token_login(form_data_mock)

        assert response_json['token_type'] == expected_token_type
        assert response_json['expires_in'] == expires_in

        # Verifica o token de acesso

        access_token = response_json['access_token']
        decoded_token = jwt.decode(
            access_token,
            secret,
            algorithms=['HS256']
        )

        assert "iat" in decoded_token and 'exp' in decoded_token
        assert len(decoded_token.keys()) == len(user_keys_to_check_in_access_token) + 2


