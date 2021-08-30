from fastapi import Depends
from server.dependencies.oauth2 import oauth2_scheme
from server.dependencies.session import get_session
from server.configuration.db import AsyncSession
from server.schemas.usuario_schema import CurrentUser
from fastapi.security import SecurityScopes
from jose import JWTError, jwt
from server.configuration import environment, exceptions
from pydantic import ValidationError
from server.schemas.token_shema import DecodedToken
from server.repository.permissao_repository import PermissaoRepository


async def get_current_user(
    required_security_permission_scopes: SecurityScopes,
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme),
) -> CurrentUser:
    """
        Verifique se o token foi expirado ou é inválido

        Verifica as permissões requeridas pelo endpoint atual
        em required_security_permission_scopes e compara com as
        permissões vinculadas às funções do usuário

        Se as condições forem satisfeitas, retorna o usuário
        atual, que fez a requisição
    """

    try:
        decoded_token_dict = jwt.decode(
            token,
            environment.ACCESS_TOKEN_SECRET_KEY,
            algorithms=[environment.ACCESS_TOKEN_ALGORITHM]
        )
        decoded_token = DecodedToken(**decoded_token_dict)
    except (JWTError, ValidationError):
        raise exceptions.InvalidExpiredTokenException()

    permission_repo = PermissaoRepository(session)
    roles = [int(role) for role in decoded_token.roles]

    user_permissions = await permission_repo.find_permissions_by_roles_list(roles)
    user_permissions_names = [permission.nome for permission in user_permissions]

    for required_permission_scope in required_security_permission_scopes.scopes:
        if required_permission_scope not in user_permissions_names:
            raise exceptions.NotEnoughPermissionsException(
                detail=f'O usuário {decoded_token.username} não tem as permissões necessárias para acessar esse recurso'
            )

    user_dict = {
        'username': decoded_token.username,
        'email': decoded_token.email,
        'guid': decoded_token.guid,
        'name': decoded_token.name,
        'roles': roles,
        'permissions': user_permissions_names
    }

    current_user = CurrentUser(**user_dict)
    return current_user
