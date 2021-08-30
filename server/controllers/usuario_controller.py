from server.schemas import usuario_schema, token_shema
from fastapi import APIRouter
from server.services.usuario_service import UsuarioService
from server.dependencies.session import get_session
from server.configuration.db import AsyncSession
from fastapi.security import HTTPBasicCredentials
from fastapi import Depends, Security
from server.controllers import session_exception_handler
from fastapi.security import SecurityScopes, OAuth2PasswordRequestForm
from server.dependencies import oauth2
from typing import List
from server.dependencies.get_current_user import get_current_user


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


@router.post("/token", response_model=token_shema.TokenOutput)
@session_exception_handler
async def get_login_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 session: AsyncSession = Depends(get_session)):
    service = UsuarioService(session)
    return await service.gera_novo_token_login(form_data)


@router.get("", response_model=List[usuario_schema.UsuarioOutput])
@session_exception_handler
async def get_all_users(
        curr_user: usuario_schema.CurrentUser = Security(get_current_user, scopes=['READ_ALL_USERS']),
        session: AsyncSession = Depends(get_session)):

    service = UsuarioService(session)
    return await service.gera_novo_token_login('q')

