"""
    Os tokens definirão scopes baseados nas FUNÇÕES dos usuários

    Os endpoints definirão scopes baseados em PERMISSÕES
    Cada FUNÇÃO pode ter várias PERMISSÕES vinculadas
"""

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/users/token'
)

