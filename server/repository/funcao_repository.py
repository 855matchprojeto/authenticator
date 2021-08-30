from server.configuration.db import async_db_session, AsyncSession
from server.models.funcao_model import Funcao
from sqlalchemy import select, insert, update, literal_column
from typing import List


class FuncaoRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def find_funcoes_by_filtros(self, filtros: List) -> List[Funcao]:
        stmt = (
            select(Funcao).
            where(*filtros)
        )
        query = await self.db_session.execute(stmt)
        return query.scalars().all()
