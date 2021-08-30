from server.configuration.db import async_db_session, AsyncSession
from server.models.permissao_model import Permissao
from server.models.vinculo_permissao_funcao_model import VinculoPermissaoFuncao
from server.models.funcao_model import Funcao
from sqlalchemy import select
from typing import List


class PermissaoRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def find_permissions_by_roles_list(self, roles: List[int]) -> List[Permissao]:
        stmt = (
            select(Permissao).
            join(
                VinculoPermissaoFuncao,
                VinculoPermissaoFuncao.id_permissao == Permissao.id
            ).
            join(
                Funcao,
                VinculoPermissaoFuncao.id_funcao == Funcao.id
            ).
            where(
                Funcao.id.in_(roles)
            )
        )
        query = await self.db_session.execute(stmt)
        return query.scalars().all()
