from fastapi import APIRouter
from server.model.usuario_model import UsuarioInput, UsuarioOutput
from server.service.usuario_service import UsuarioService
from server.dependencies.session import get_session
from server.configuration.db import AsyncSession
from fastapi.security import HTTPBasicCredentials
from fastapi import Depends
from server.controller import session_exception_handler

router = APIRouter()
usuario_router = dict(
    router=router,
    prefix="/usuarios",
    tags=["Usuários"],
)


@router.post("", response_model=UsuarioOutput)
@session_exception_handler
async def post_novo_usuario(usuario_input: UsuarioInput, session: AsyncSession = Depends(get_session)):
    service = UsuarioService(session)
    return await service.cria_novo_usuario(usuario_input)

