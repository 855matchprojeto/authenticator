import uuid
import pytest
import time

from datetime import datetime, timedelta
from server.services.usuario_service import UsuarioService
from jose import jwt, JWTError
from mock import Mock, AsyncMock
from server.configuration import exceptions
from pydantic import EmailStr

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
def single_user_arr_email_nao_verificado_db():
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
def single_user_arr_email_verificado_db():
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


@pytest.fixture
def verify_email_token_valid():
    """
        Retorna um token de verificação de e-mail codificado pelo
        secret_key "secret" e algoritmo "HS256"
    """

    data_to_encode = dict(
        email="teste@unicamp.br",
        username="user",
        name="Teste"
    )

    return jwt.encode(
        data_to_encode,
        "secret",
        algorithm="HS256"
    )


@pytest.fixture
def verify_email_token_expired():
    """
        Retorna um token de verificação de e-mail codificado pelo
        secret_key "secret" e algoritmo "HS256".
        O tempo de expiração desse token é expirado!
    """

    timestamp_atual = datetime.utcnow()
    timestamp_exp = timestamp_atual - timedelta(seconds=1)

    data_to_encode = dict(
        email="teste@unicamp.br",
        username="user",
        name = "Teste",
        exp=timestamp_exp
    )

    return jwt.encode(
        data_to_encode,
        "secret",
        algorithm="HS256"
    )


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
    @pytest.mark.parametrize("email_valido_unicamp", [
        "teste@dac.unicamp.br",
        "teste@students.ic.unicamp.br",
        "teste@unicamp.br"
    ])
    def test_valida_email_unicamp_valido(email_valido_unicamp: EmailStr):
        """
            Valida se a função reconhece emails válidos da Unicamp
            Obs: A função já recebe EmailStr
        """
        assert UsuarioService.valida_email_unicamp(email_valido_unicamp)

    @staticmethod
    @pytest.mark.parametrize("email_invalido_unicamp", [
        "teste@gmail.com",
        "teste@unicamp.com",
        "teste@unicamp.br.com",
        "teste@unicamp.br.",
    ])
    def test_valida_email_unicamp_invalido(email_invalido_unicamp: EmailStr):
        """
            Valida se a função reconhece emails inválidos, que não pertencem ao
            domínio da unicamp
            Obs: A função já recebe EmailStr
        """
        assert not UsuarioService.valida_email_unicamp(email_invalido_unicamp)

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
    async def test_gera_novo_token_login_invalid_password(single_user_arr_email_verificado_db):
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
        user_repo_mock.find_usuarios_by_filtros = AsyncMock(return_value=single_user_arr_email_verificado_db)

        service = UsuarioService(
            user_repo=user_repo_mock
        )

        with pytest.raises(exceptions.InvalidUsernamePasswordException):
            await service.gera_novo_token_login(form_data_mock)

    @staticmethod
    @pytest.mark.asyncio
    async def test_gera_novo_token_login_email_nao_confirmado(single_user_arr_email_nao_verificado_db):
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
        user_repo_mock.find_usuarios_by_filtros = AsyncMock(return_value=single_user_arr_email_nao_verificado_db)

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
            single_user_arr_email_verificado_db, user_keys_to_check_in_access_token,
            expected_token_type, secret, expires_in):
        """
            O repository retorna um array unitário mockado.
            O usuário retornado tem o hash da senha "pass".
            Será enviada uma senha errada de propósito e é
            esperado que seja retornada uma exceção
        """

        user = single_user_arr_email_verificado_db[0]

        form_data_mock = Mock()
        form_data_mock.username = "user"
        form_data_mock.password = "pass"

        user_repo_mock = Mock()
        user_repo_mock.find_usuarios_by_filtros = AsyncMock(return_value=single_user_arr_email_verificado_db)

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

    @staticmethod
    @pytest.mark.parametrize("email", [
        "s@hotmail.com",
        "ad@gmail.com",
        "a@unicamp.br.",
        "a@.unicamp.br."
    ])
    @pytest.mark.asyncio
    async def test_cria_novo_usuario_email_invalido(email):

        usuario_input_mock = Mock()
        usuario_input_mock.email = email

        service = UsuarioService()

        with pytest.raises(exceptions.InvalidEmailException):
            await service.cria_novo_usuario(usuario_input_mock)

    @staticmethod
    @pytest.mark.parametrize("nome, password, email", [
        ("Teste", "pass", "teste@unicamp.br")
    ])
    @pytest.mark.asyncio
    async def test_cria_novo_usuario_username_conflict(single_user_arr_email_nao_verificado_db, nome,
                                                       password, email):

        usuario_input_mock = Mock()
        usuario_input_mock.email = email
        usuario_input_mock.username = single_user_arr_email_nao_verificado_db[0].username
        usuario_input_mock.nome = nome
        usuario_input_mock.password = password

        user_repo_mock = Mock()
        user_repo_mock.find_usuarios_by_filtros = AsyncMock(
            return_value=single_user_arr_email_nao_verificado_db
        )

        service = UsuarioService(
            user_repo=user_repo_mock
        )

        with pytest.raises(exceptions.UsernameConflictException):
            await service.cria_novo_usuario(usuario_input_mock)

    @staticmethod
    @pytest.mark.parametrize("username, nome, password", [
        ("userdiff", "Teste", "pass")
    ])
    @pytest.mark.asyncio
    async def test_cria_novo_usuario_email_conflict(single_user_arr_email_nao_verificado_db, nome,
                                                    password, username):
        usuario_input_mock = Mock()
        usuario_input_mock.email = single_user_arr_email_nao_verificado_db[0].email
        usuario_input_mock.username = username
        usuario_input_mock.nome = nome
        usuario_input_mock.password = password

        user_repo_mock = Mock()
        user_repo_mock.find_usuarios_by_filtros = AsyncMock(
            return_value=single_user_arr_email_nao_verificado_db
        )

        service = UsuarioService(
            user_repo=user_repo_mock
        )

        with pytest.raises(exceptions.EmailConflictException):
            await service.cria_novo_usuario(usuario_input_mock)

    @staticmethod
    @pytest.mark.parametrize("username, nome, password, email", [
        ("user1", "Teste", "pass", "teste@unicamp.br"),
        ("user2", "Teste2", "pass2", "teste@students.ic.unicamp.br")
    ])
    @pytest.mark.asyncio
    async def test_cria_novo_usuario_email_conflict(empty_arr, nome,
                                                    password, username, email):

        usuario_input_mock = Mock()
        usuario_input_mock.email = email
        usuario_input_mock.username = username
        usuario_input_mock.nome = nome
        usuario_input_mock.password = password

        usuario_input_mock.convert_to_dict = Mock(
            return_value=dict(
                username=username,
                password=password,
                nome=nome,
                email=email
            )
        )

        user_repo_mock = Mock()
        user_repo_mock.find_usuarios_by_filtros = AsyncMock(
            return_value=empty_arr
        )
        user_repo_mock.insere_usuario = AsyncMock(return_value=None)

        service = UsuarioService(
            user_repo=user_repo_mock
        )

        await service.cria_novo_usuario(usuario_input_mock)

    @staticmethod
    @pytest.mark.parametrize("username", [
        "user"
    ])
    @pytest.mark.asyncio
    async def test_send_email_verification_link_user_not_found(empty_arr, username):

        user_repo_mock = Mock()
        user_repo_mock.find_usuarios_by_filtros = AsyncMock(
            return_value=empty_arr
        )

        service = UsuarioService(
            user_repo=user_repo_mock
        )

        with pytest.raises(exceptions.UserNotFoundException):
            await service.send_email_verification_link(username)

    @staticmethod
    @pytest.mark.parametrize("username", [
        "user"
    ])
    @pytest.mark.asyncio
    async def test_send_email_verification_link_email_already_confirmed(single_user_arr_email_verificado_db, username):
        user_repo_mock = Mock()
        user_repo_mock.find_usuarios_by_filtros = AsyncMock(
            return_value=single_user_arr_email_verificado_db
        )

        service = UsuarioService(
            user_repo=user_repo_mock
        )

        with pytest.raises(exceptions.EmailAlreadyConfirmedException):
            await service.send_email_verification_link(username)

    @staticmethod
    @pytest.mark.parametrize("username", [
        "user"
    ])
    @pytest.mark.asyncio
    async def test_send_email_verification_link_email_email_not_confirmed(single_user_arr_email_nao_verificado_db, username):

        user_repo_mock = Mock()
        user_repo_mock.find_usuarios_by_filtros = AsyncMock(
            return_value=single_user_arr_email_nao_verificado_db
        )

        environment_mock = Mock(
            MAIL_TOKEN_EXPIRE_DELTA_IN_SECONDS=3600,
            MAIL_TOKEN_SECRET_KEY="secret",
            MAIL_TOKEN_ALGORITHM="HS256",
            SERVER_DNS="SERVER_DNS"
        )

        email_sender_service_mock = Mock()
        email_sender_service_mock.send_email_background = Mock(return_value=None)

        service = UsuarioService(
            user_repo=user_repo_mock,
            environment=environment_mock,
            email_sender_service=email_sender_service_mock
        )

        await service.send_email_verification_link(username)

        email_sender_service_mock.send_email_background.assert_called()

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_email_invalid_token_secret(verify_email_token_valid):

        environment_mock = Mock(
            MAIL_TOKEN_SECRET_KEY="wrong-secret",
            MAIL_TOKEN_ALGORITHM="HS256"
        )

        service = UsuarioService(
            environment=environment_mock
        )

        with pytest.raises(exceptions.InvalidExpiredTokenException):
            await service.verify_email(None, verify_email_token_valid)

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_email_expired_token(verify_email_token_expired):

        environment_mock = Mock(
            MAIL_TOKEN_SECRET_KEY="secret",
            MAIL_TOKEN_ALGORITHM="HS256"
        )

        service = UsuarioService(
            environment=environment_mock
        )

        with pytest.raises(exceptions.InvalidExpiredTokenException):
            await service.verify_email(None, verify_email_token_expired)

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_email_user_not_found(verify_email_token_valid, empty_arr):

        environment_mock = Mock(
            MAIL_TOKEN_SECRET_KEY="secret",
            MAIL_TOKEN_ALGORITHM="HS256"
        )

        user_repo_mock = Mock()
        user_repo_mock.find_usuarios_by_filtros = AsyncMock(
            return_value=empty_arr
        )

        service = UsuarioService(
            environment=environment_mock,
            user_repo=user_repo_mock
        )

        with pytest.raises(exceptions.InvalidExpiredTokenException):
            await service.verify_email(None, verify_email_token_valid)

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_email(verify_email_token_valid, single_user_arr_email_nao_verificado_db):

        environment_mock = Mock(
            MAIL_TOKEN_SECRET_KEY="secret",
            MAIL_TOKEN_ALGORITHM="HS256"
        )

        user_repo_mock = Mock()
        user_repo_mock.find_usuarios_by_filtros = AsyncMock(
            return_value=single_user_arr_email_nao_verificado_db
        )
        user_repo_mock.verify_email = AsyncMock(
            return_value=None
        )

        service = UsuarioService(
            environment=environment_mock,
            user_repo=user_repo_mock
        )

        await service.verify_email(None, verify_email_token_valid)

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_all_users(single_user_arr_email_nao_verificado_db):

        user_repo_mock = Mock()
        user_repo_mock.find_usuarios_by_filtros = AsyncMock(
            return_value=single_user_arr_email_nao_verificado_db
        )

        service = UsuarioService(
            user_repo=user_repo_mock
        )

        await service.get_all_users()

