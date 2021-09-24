from server.configuration.db import AsyncSession
from server.models.funcao_model import Funcao
from sqlalchemy import select
from typing import List, Optional
from server.configuration.environment import Environment
from sqlalchemy.orm import selectinload


class FuncaoRepository:

    def __init__(self, db_session: AsyncSession, environment: Optional[Environment]):
        self.db_session = db_session
        self.environment = environment

    async def find_funcoes_by_filtros(self, filtros: List) -> List[Funcao]:
        stmt = (
            select(Funcao).
            where(*filtros).
            options(
                selectinload(Funcao.vinculos_permissao_funcao),
            )
        )
        query = await self.db_session.execute(stmt)
        return query.scalars().all()
