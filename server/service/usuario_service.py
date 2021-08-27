from server.repository.usuario_repository import UsuarioRepository
from server.configuration.db import AsyncSession
from server.model.usuario_model import UsuarioInput, UsuarioOutput, Usuario
from fastapi.security import HTTPBasicCredentials
import re
from server.configuration import exceptions
from sqlalchemy import or_
from passlib.context import CryptContext


class UsuarioService:

    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.unicamp\.br\b'

    @staticmethod
    def valida_email_unicamp(email: str):
        return re.match(UsuarioService.email_regex, email)

    def verifica_senha(self, password, hashed_password):
        return self.crypt_context.verify(password, hashed_password)

    def criptografa_senha(self, password):
        return self.crypt_context.hash(password)

    def __init__(self, db_session: AsyncSession):
        self.repo = UsuarioRepository(db_session)
        self.crypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

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

        x = await self.repo.insere_usuario(novo_usuario_dict)
        return x

