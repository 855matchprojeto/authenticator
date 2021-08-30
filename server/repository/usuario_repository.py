from server.configuration.db import AsyncSession
from server.models.usuario_model import Usuario
from server.models.vinculo_usuario_funcao_model import VinculoUsuarioFuncao
from server.models.vinculo_permissao_funcao_model import VinculoPermissaoFuncao
from sqlalchemy.orm import selectinload, join
from sqlalchemy import select, insert, update, literal_column
from typing import List


class UsuarioRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

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
                selectinload(Usuario.funcoes)
            )
        )
        query = await self.db_session.execute(stmt)
        return query.scalars().all()

