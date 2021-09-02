"""
    Módulo responsável por armazenar a primeira camada de acesso à aplicação

    Nos controllers são definidas as rotas e endpoints, além das especificações
    dos mesmos
"""

from server.configuration.db import AsyncSession
from functools import wraps


def session_exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        session: AsyncSession = kwargs['session']
        try:
            result = await func(*args, **kwargs)
            await session.commit()
            return result
        except Exception as ex:
            await session.rollback()
            raise ex
        finally:
            await session.close()
    return wrapper

