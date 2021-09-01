from server.repository.usuario_repository import UsuarioRepository
from server.configuration.db import AsyncSession
from server.schemas.usuario_schema import UsuarioInput, UsuarioOutput
from server.models.usuario_model import Usuario
import re
from server.configuration import exceptions, environment
from sqlalchemy import or_, and_
from passlib.context import CryptContext
from jose import JWTError, jwt
from server.schemas.token_shema import DecodedMailToken
from datetime import timedelta
from datetime import datetime
from typing import List
from fastapi.security import OAuth2PasswordRequestForm
from server.services.email_service import EmailService
from fastapi import BackgroundTasks, Request
from fastapi_mail import ConnectionConfig
from pydantic import ValidationError
from server.templates import jinja2_templates


class UsuarioService:

    EMAIL_SENDER_CONFIG = ConnectionConfig(
        MAIL_USERNAME=environment.MAIL_USERNAME,
        MAIL_PASSWORD=environment.MAIL_PASSWORD,
        MAIL_FROM=environment.MAIL_FROM,
        MAIL_PORT=environment.MAIL_PORT,
        MAIL_SERVER=environment.MAIL_SERVER,
        MAIL_TLS=environment.MAIL_TLS,
        MAIL_SSL=environment.MAIL_SSL,
        USE_CREDENTIALS=environment.MAIL_USE_CREDENTIALS,
        TEMPLATE_FOLDER='./templates'
    )

    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]*unicamp\.br\b'

    @staticmethod
    def valida_email_unicamp(email: str):
        return re.match(UsuarioService.email_regex, email)

    def verifica_senha(self, password: str, hashed_password: str) -> bool:
        return self.crypt_context.verify(password, hashed_password)

    def criptografa_senha(self, password: str) -> str:
        return self.crypt_context.hash(password)

    def gena_token(self, data_to_encode: dict, expires_delta: timedelta,
                          secret_key: str, algorithm: str):
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
            secret_key,
            algorithm=algorithm
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

    async def verify_email(self, request: Request, code: str):
        """
            No email de verificação é enviado uma query
            string 'code' com o token criado pelo servidor.

            Nesse endpoint, o token é decodificado e é verificado
            se é valido e se não foi expirado.

            Caso a verificação seja bem sucedida, o usuário relacionado
            o usuário é marcado como 'email_verificado' no banco
        """

        try:
            decoded_token_dict = jwt.decode(
                code,
                environment.MAIL_TOKEN_SECRET_KEY,
                algorithms=[environment.MAIL_TOKEN_ALGORITHM]
            )
            decoded_token = DecodedMailToken(**decoded_token_dict)
        except (JWTError, ValidationError):
            raise exceptions.InvalidExpiredTokenException()

        # Verificando se o usuário de fato existe no banco de dados

        filtros = [
            and_(
                Usuario.email == decoded_token.email,
                Usuario.username == decoded_token.username
            )
        ]

        user_list = await self.repo.find_usuarios_by_filtros(filtros)
        if len(user_list) == 0:
            raise exceptions.InvalidExpiredTokenException()
        user = user_list[0]

        # Marca o email como confirmado

        await self.repo.verify_email(user)

        # Enviando um HTML de resposta

        return jinja2_templates.TemplateResponse(
            'email_confirmed_body_template.html',
            {
                'request': request,
                'user': {
                    'name': user.nome,
                    'email': user.email,
                    'username': user.username
                }
            }
        )

    async def send_email_verification_link(self, username: str, background_tasks: BackgroundTasks):
        """
            Função responsável por enviar o email de verificação
            para confirmar o e-mail do usuário.

            Gera um token com um tempo de expiração bem-definido
            Esse token vai ser adicionado na query string de uma URL
            que é tratada pelo servidor no endpoint /users/verify-email

            Essa URL é enviada no e-mail para que o usuário clique no link
            e confirme de fato seu e-mail
        """

        user_list = await self.repo.find_usuarios_by_filtros([Usuario.username == username])
        if len(user_list) == 0:
            raise exceptions.UserNotFoundException(
                detail=f'Não foi encontrado um usuário {username}'
            )

        user = user_list[0]
        if user.email_verificado:
            raise exceptions.EmailAlreadyConfirmedException(
                detail=f'O e-mail {user.email} já foi confirmado pelo sistema'
            )

        # Construindo o objeto para ser codificado
        # Constitui um token que será inserido no link para
        # confirmar o e-mail do usuário

        email_token_before_encode = {
            'name': user.nome,
            'email': user.email,
            'username': user.username
        }

        email_token_expire_delta = timedelta(
            seconds=environment.MAIL_TOKEN_EXPIRE_DELTA_IN_SECONDS
        )

        email_token = self.gena_token(
            data_to_encode=email_token_before_encode,
            expires_delta=email_token_expire_delta,
            secret_key=environment.MAIL_TOKEN_SECRET_KEY,
            algorithm=environment.MAIL_TOKEN_ALGORITHM
        )

        # Enviando o email em background e gerando um link para o usuário
        # clicar, com o token. Esse servidor implementará um
        # GET que trata essa URL, confirmando o e-mail

        email_service = EmailService(
            UsuarioService.EMAIL_SENDER_CONFIG,
            background_tasks
        )

        email_service.send_email_background(
            recipient_email_list=[user.email],
            subject="Plataforma de Match de Projetos - Verificação de Email",
            template_name='verify_email_template.html',
            template_body={
                'user': {
                    'email': user.email,
                    'name': user.nome,
                    'username': user.username
                },
                'expires_in_hours': environment.MAIL_TOKEN_EXPIRE_DELTA_IN_SECONDS//3600,
                'verify_link': f'{environment.SERVER_DNS}/users/verify-email?code={email_token}'
            }
        )

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

        access_token = self.gena_token(
            data_to_encode=access_token_before_encode,
            expires_delta=access_token_expire_delta,
            secret_key=environment.ACCESS_TOKEN_SECRET_KEY,
            algorithm=environment.ACCESS_TOKEN_ALGORITHM
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

