from server.schemas import usuario_schema
from fastapi import APIRouter
from server.services.usuario_service import UsuarioService
from server.dependencies.session import get_session
from server.configuration.db import AsyncSession
from fastapi.security import HTTPBasicCredentials
from fastapi import Depends
from server.controllers import session_exception_handler

router = APIRouter()
usuario_router = dict(
    router=router,
    prefix="/usuarios",
    tags=["Usuários"],
)

@router.post("", response_model=usuario_schema.UsuarioOutput)
@session_exception_handler
async def post_novo_usuario(usuario_input: usuario_schema.UsuarioInput, session: AsyncSession = Depends(get_session)):
    service = UsuarioService(session)
    return await service.cria_novo_usuario(usuario_input)

