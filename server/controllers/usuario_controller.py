from server.schemas import usuario_schema, token_shema
from fastapi import APIRouter, Request, Response
from server.services.usuario_service import UsuarioService
from server.dependencies.session import get_session
from server.dependencies.get_environment_cached import get_environment_cached
from server.configuration.db import AsyncSession
from fastapi import Depends, Security
from server.controllers import session_exception_handler
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from server.dependencies.get_current_user import get_current_user
from server.constants.permission import RoleBasedPermission
from fastapi.responses import HTMLResponse
from fastapi import status
from server.repository.usuario_repository import UsuarioRepository
from server.configuration.environment import Environment
from server.services.email_service import EmailService
from server.dependencies.get_email_sender_service_cached import get_email_sender_service_cached


router = APIRouter()
usuario_router = dict(
    router=router,
    prefix="/users",
    tags=["Usuários"],
)


@router.get("", response_model=List[usuario_schema.UsuarioOutput])
@session_exception_handler
async def get_all_users(
        _: usuario_schema.CurrentUser = Security(get_current_user, scopes=[RoleBasedPermission.READ_ALL_USERS['name']]),
        session: AsyncSession = Depends(get_session), environment: Environment = Depends(get_environment_cached)):

    service = UsuarioService(
        UsuarioRepository(session, environment),
        environment
    )
    return await service.get_all_users()


@router.post("", response_model=usuario_schema.UsuarioOutput)
@session_exception_handler
async def post_novo_usuario(usuario_input: usuario_schema.UsuarioInput, session: AsyncSession = Depends(get_session),
                            environment: Environment = Depends(get_environment_cached)):

    service = UsuarioService(
        UsuarioRepository(session, environment),
        environment
    )
    return await service.cria_novo_usuario(usuario_input)


@router.post("/token", response_model=token_shema.AccessTokenOutput)
@session_exception_handler
async def get_login_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 session: AsyncSession = Depends(get_session),
                                 environment: Environment = Depends(get_environment_cached)):

    service = UsuarioService(
        UsuarioRepository(session, environment),
        environment
    )
    return await service.gera_novo_token_login(form_data)


@router.post("/{username}/send-email-verification-link", status_code=status.HTTP_204_NO_CONTENT)
@session_exception_handler
async def send_email_verification_link(
        username: str,
        session: AsyncSession = Depends(get_session),
        environment: Environment = Depends(get_environment_cached),
        email_sender_service: EmailService = Depends(get_email_sender_service_cached)
):

    service = UsuarioService(
        UsuarioRepository(session, environment),
        environment,
        email_sender_service
    )
    await service.send_email_verification_link(username)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/verify-email", include_in_schema=False, response_class=HTMLResponse)
@session_exception_handler
async def verify_email(request: Request, code: str, session: AsyncSession = Depends(get_session),
                       environment: Environment = Depends(get_environment_cached)):

    service = UsuarioService(
        UsuarioRepository(session, environment),
        environment
    )
    return await service.verify_email(request, code)

