from server.configuration.db import AsyncSession
from server.models.usuario_model import Usuario
from sqlalchemy.orm import selectinload
from sqlalchemy import select, insert, literal_column
from typing import List, Optional
from server.configuration.environment import Environment


class UsuarioRepository:

    def __init__(self, db_session: AsyncSession, environment: Optional[Environment] = None):
        self.db_session = db_session
        self.environment = environment

    async def insere_usuario(self, usuario_dict: dict) -> Usuario:
        stmt = (
            insert(Usuario).
            returning(literal_column('*')).
            values(**usuario_dict)
        )
        query = await self.db_session.execute(stmt)
        row_to_dict = dict(query.fetchone())
        return Usuario(**row_to_dict)

    async def insere_usuario_2(self, usuario_dict: dict) -> Usuario:
        new_user_entity = Usuario(**usuario_dict)
        self.db_session.add(new_user_entity)
        await self.db_session.flush()
        return new_user_entity

    async def find_usuarios_by_filtros(self, filtros: List) -> List[Usuario]:
        stmt = (
            select(Usuario).
            where(*filtros).
            options(
                selectinload(Usuario.vinculos_usuario_funcao)
            )
        )
        query = await self.db_session.execute(stmt)
        return query.scalars().all()

    async def find_usuario_by_guid(self, guid_usuario: str) -> List[Usuario]:
        stmt = (
            select(Usuario).
            where(Usuario.guid == guid_usuario)
        )
        query = await self.db_session.execute(stmt)
        return query.scalars().first()

    async def verify_email(self, user: Usuario) -> Usuario:
        user.email_verificado = True
        await self.db_session.flush()
        return user
