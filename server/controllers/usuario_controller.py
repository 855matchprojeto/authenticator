from server.schemas import usuario_schema, token_shema
from fastapi import APIRouter, Request, Response
from server.services.usuario_service import UsuarioService
from server.dependencies.session import get_session
from server.dependencies.get_environment_cached import get_environment_cached
from server.configuration.db import AsyncSession
from fastapi import Depends, Security
from server.controllers import endpoint_exception_handler
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from server.dependencies.get_current_user import get_current_user
from server.constants.permission import RoleBasedPermission
from fastapi.responses import HTMLResponse
from fastapi import status
from server.repository.usuario_repository import UsuarioRepository
from server.configuration.environment import Environment
from server.services.email_service import EmailService
from server.dependencies.get_email_sender_service import get_email_sender_service
from server.schemas import error_schema
from server.dependencies.get_sns_publisher_service import get_sns_publisher_service
from server.services.aws_publisher_service import AWSPublisherService
import boto3


router = APIRouter()
usuario_router = dict(
    router=router,
    prefix="/users",
    tags=["Usuários"],
)


@router.get(
    "",
    response_model=List[usuario_schema.UsuarioOutput],
    summary='Retorna todos os usuários registrados no microsserviço de autenticação',
    response_description='Lista dos usuários retornados',
    responses={
        401: {
            'model': error_schema.ErrorOutput401,
        },
        422: {
            'model': error_schema.ErrorOutput422,
        },
        500: {
            'model': error_schema.ErrorOutput500
        }
    }
)
@endpoint_exception_handler
async def get_all_users(
    _: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[RoleBasedPermission.READ_ALL_USERS['name']]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Retorna todos os usuários registrados no microsserviço de autenticação.

        # Permissões

        Para acessar esse endpoint é necessário que o usuário seja vinculado à funções
        especiais no sistema.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(NOT_ENOUGH_PERMISSION, 401)**: A sessão atual do usuário não permite que o usuário acesse o
        recurso.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    service = UsuarioService(
        UsuarioRepository(session, environment),
        environment
    )
    return await service.get_all_users()


@router.get(
    "/me",
    response_model=usuario_schema.CurrentUserOutput,
    summary='Retorna as informações contidas no token do usuário',
    response_description='Informações contidas no token do usuário',
    responses={
        401: {
            'model': error_schema.ErrorOutput401,
        },
        422: {
            'model': error_schema.ErrorOutput422,
        },
        500: {
            'model': error_schema.ErrorOutput500
        }
    }
)
@endpoint_exception_handler
async def get_current_user(
    current_user: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
):

    """
        # Descrição

        Retorna as informações do usuário atual vinculadas ao token.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    return UsuarioService.current_user_output(current_user)


@router.post(
    "",
    response_model=usuario_schema.UsuarioOutput,
    summary='Cria um novo usuário',
    response_description='Usuário criado',
    responses={
        404: {
            'model': error_schema.ErrorOutput404
        },
        409: {
            'model': error_schema.ErrorOutput409
        },
        422: {
            'model': error_schema.ErrorOutput422
        },
        500: {
            'model': error_schema.ErrorOutput500
        }
    }
)
@endpoint_exception_handler
async def post_novo_usuario(
    usuario_input: usuario_schema.UsuarioInput,
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
    publisher_service: AWSPublisherService = Depends(get_sns_publisher_service)
):

    """
        # Descrição

        Cria um novo usuário a partir das informações enviadas no corpo da requisição.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(USERNAME_ALREADY_EXISTS, 409)**: Nome de usuário já está cadastrado no sistema.
        - **(EMAIL_ALREADY_EXISTS, 409)**: E-mail já está cadastrado no sistema.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INVALID_EMAIL, 422)**: E-mail não pertence ao domínio da UNICAMP.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    service = UsuarioService(
        UsuarioRepository(session, environment),
        environment,
        publisher_service=publisher_service
    )
    return await service.cria_novo_usuario(usuario_input)


@router.post(
    "/token",
    response_model=token_shema.AccessTokenOutput,
    summary='Endpoint de login',
    response_description='Retorno do token de acesso e suas especificações',
    responses={
        403: {
            'model': error_schema.ErrorOutput403
        },
        422: {
            'model': error_schema.ErrorOutput422
        },
        500: {
            'model': error_schema.ErrorOutput500
        }
    }
)
@endpoint_exception_handler
async def get_login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached)
):

    """
        # Descrição

        Endpoint responsável pela implementação de login no sistema.

        É retornado um token de acesso ao usuário. O tempo de expiração desse token
        também é retornado na resposta da requisição.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(EMAIL_NOT_CONFIRMED, 401)**: E-mail ainda não foi confirmado pelo usuário.
        - **(INVALID_USERNAME_OR_PASSWORD, 403)**: Esse erro é apresentado nos seguintes cenários:
            - Senha inválida
            - Usuário não encontrado no sistema
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    service = UsuarioService(
        UsuarioRepository(session, environment),
        environment
    )
    return await service.gera_novo_token_login(form_data)


@router.post(
    "/send-email-verification-link/{username}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Envia um email de verificação ao usuário',
    responses={
        404: {
            'model': error_schema.ErrorOutput404
        },
        422: {
            'model': error_schema.ErrorOutput422
        },
        500: {
            'model': error_schema.ErrorOutput500
        }
    }
)
@endpoint_exception_handler
async def send_email_verification_link(
    username: str,
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
    email_sender_service: EmailService = Depends(get_email_sender_service)
):
    """
        # Descrição

        Envia um email de verificação ao usuário contendo um link de verificação.
        Nesse link, há um token criado por esse endpoint.

        Note que o e-mail é enviado de maneira assíncrona. O endpoint retorna o sucesso
        mesmo sem saber se o e-mail foi enviado.

        Quando o usuário clicar no link, o e-mail do usuário é confirmado.

         # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(USER_NOT_FOUND, 404)**: Usuário não encontrado.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(EMAIL_ALREADY_CONFIRMED, 422)**: Email já foi confirmado pelo sistema.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    service = UsuarioService(
        UsuarioRepository(session, environment),
        environment,
        email_sender_service
    )
    await service.send_email_verification_link(username)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/verify-email",
    include_in_schema=False,
    response_class=HTMLResponse
)
@endpoint_exception_handler
async def verify_email(
    request: Request, code: str,
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached)
):

    service = UsuarioService(
        UsuarioRepository(session, environment),
        environment
    )
    return await service.verify_email(request, code)


@router.get(
    "/{guid_usuario}",
    response_model=usuario_schema.UsuarioOutput,
    summary='Cria um perfil e um usuário na tabela de usuário (neste microserviço)',
    response_description='Cria um perfil e um usuário na tabela de usuário (neste microserviço)',
    include_in_schema=True,
    responses={
        401: {
            'model': error_schema.ErrorOutput401,
        },
        404: {
            'model': error_schema.ErrorOutput404,
        },
        422: {
            'model': error_schema.ErrorOutput422,
        },
        500: {
            'model': error_schema.ErrorOutput500
        }
    }
)
@endpoint_exception_handler
async def get_user_by_guid(
    guid_usuario: str,
    _: usuario_schema.CurrentUserToken = Security(
        get_current_user, scopes=[RoleBasedPermission.READ_ALL_USERS['name']]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Captura um usuário e suas informações através de seu GUID. Apenas usuários com cargos com permissão
        'READ_ALL_USERS' (Leitura de qualquer usuário) possuem a autorização para acessar essa requisiçõo.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    usuario_service = UsuarioService(
        user_repo=UsuarioRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment
    )

    return await usuario_service.get_user_by_guid(guid_usuario)

