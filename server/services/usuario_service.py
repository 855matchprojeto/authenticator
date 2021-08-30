from server.repository.usuario_repository import UsuarioRepository
from server.configuration.db import AsyncSession
from server.schemas.usuario_schema import UsuarioInput, UsuarioOutput
from server.models.usuario_model import Usuario
import re
from server.configuration import exceptions
from sqlalchemy import or_
from passlib.context import CryptContext
from server.dependencies import oauth2
from jose import JWTError, jwt
from server.schemas.token_shema import TokenOutput
from datetime import timedelta
from server.configuration import environment
from datetime import datetime
from typing import List
from fastapi.security import OAuth2PasswordRequestForm


class UsuarioService:

    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]*unicamp\.br\b'

    @staticmethod
    def valida_email_unicamp(email: str):
        return re.match(UsuarioService.email_regex, email)

    def verifica_senha(self, password: str, hashed_password: str) -> bool:
        return self.crypt_context.verify(password, hashed_password)

    def criptografa_senha(self, password: str) -> str:
        return self.crypt_context.hash(password)

    def gena_access_token(self, data_to_encode: dict, expires_delta: timedelta):
        """
            Função responsável por atualizar o objeto à ser codificado
            adicionando duas informações adicionais:
            - Timestamp do momento de criacao (iat - issued at)
            - Timestamp de expiracao (exp - expiration)
            Ao fim, é codificado utilizando as chaves e algoritmos
            definidos na variável de ambiente do servidor
        """

        # Capturando o timestamp atual e definindo o timestamp de expiracao

        timestamp_atual = datetime.utcnow()
        timestamp_exp = timestamp_atual + expires_delta

        data_to_encode.update(
            {'iat': timestamp_atual, 'exp': timestamp_exp}
        )

        # Retornando o objeto codificado

        return jwt.encode(
            data_to_encode,
            environment.ACCESS_TOKEN_SECRET_KEY,
            algorithm=environment.ACCESS_TOKEN_ALGORITHM
        )

    def __init__(self, db_session: AsyncSession):
        self.repo: UsuarioRepository = UsuarioRepository(db_session)
        self.crypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    async def autentica_usuario(self, username: str, password: str):
        """
            Função responsável por autenticar o usuário
            É verificado se o usuário existe e se a senha está correta
        """

        user: List[Usuario] = await self.repo.find_usuarios_by_filtros([Usuario.username == username])
        if len(user) == 0 or not self.verifica_senha(password, user[0].hashed_password):
            raise exceptions.InvalidUsernamePasswordException()

        return user[0]

    async def get_all_users(self):
        return await self.repo.find_usuarios_by_filtros(filtros=[])

    async def gera_novo_token_login(self, form_data: OAuth2PasswordRequestForm) -> dict:
        """
            Função responsável por autenticar o usuário com a informação do form
            e verificar se o e-mail foi verificado.
            Validando esses dois cenários, é gerado um novo access_token para o usuário,
            contendo

        :param form_data: Dados de usuário e senha enviados a partir do requestForm
        :return: Objeto de tokenOutput como definido no schema
        """

        # Autenticando e verificando se e-mail foi confirmado

        user = await self.autentica_usuario(form_data.username, form_data.password)
        if not user.email_verificado:
            raise exceptions.InvalidEmailException(
                detail=f'O email {user.email} ainda não foi verificado'
            )

        # Construindo o objeto para ser codificado

        access_token_before_encode = {
            'guid': str(user.guid),
            'name': user.nome,
            'email': user.email,
            'username': user.username,
            'roles': (
                [funcao.id for funcao in user.funcoes]
            )
        }

        # Com o usuário autenticado, basta gerar um novo jwt com tempo de expiração bem definido

        access_token_expire_delta = timedelta(
            seconds=environment.ACCESS_TOKEN_EXPIRE_DELTA_IN_SECONDS
        )

        access_token = self.gena_access_token(
            data_to_encode=access_token_before_encode,
            expires_delta=access_token_expire_delta
        )

        return {
            'token_type': 'Bearer',
            'expires_in': environment.ACCESS_TOKEN_EXPIRE_DELTA_IN_SECONDS,
            'access_token': access_token
        }

    async def cria_novo_usuario(self, usuario_input: UsuarioInput) -> UsuarioOutput:
        """
            Função responsável por validar o usuário:
               - Email unicamp
               - Não existe username e e-mail na base de dados
            E armazenar o usuário com a senha criptografada

        :param usuario_input: Body da requisição com informações como email e nome
        :return: Usuário criado pelo banco de dados no formato 'UsuarioOutput'
        """

        email = usuario_input.email

        # Valida email da unicamp

        match = UsuarioService.valida_email_unicamp(email)
        if not match:
            raise exceptions.InvalidEmailException(
                detail=f"O e-mail ({email}) não é um e-mail válido da UNICAMP. "
                       f"Verifique se o e-mail contém (.unicamp.br) e tente novamente"
            )

        # Valida usuário na base de dados
        # Não pode haver um usuário com mesmo usuário ou e-mail

        filtros = [
            or_(
                Usuario.email == usuario_input.email,
                Usuario.username == usuario_input.username
            )
        ]

        usuarios_db = await self.repo.find_usuarios_by_filtros(filtros)

        if len(usuarios_db):
            conflict_user = usuarios_db[0]
            if conflict_user.username == usuario_input.username:
                raise exceptions.UsernameConflictException(
                    detail=f"Já existe um usuário com o nome de usuário ({conflict_user.username})"
                )
            else:
                raise exceptions.EmailConflictException(
                    detail=f"Já existe um usuário com o e-mail ({conflict_user.email})"
                )

        # Aplica hashing na senha do usuário e cria o objeto do novo usuário
        # para inserção no banco de dados

        novo_usuario_dict = usuario_input.convert_to_dict()
        novo_usuario_dict['hashed_password'] = self.criptografa_senha(usuario_input.password)
        del novo_usuario_dict['password']

        # Insere no banco de dados e retorna o usuário

        return await self.repo.insere_usuario(novo_usuario_dict)

