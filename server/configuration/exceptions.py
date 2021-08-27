from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse


class ApiBaseException(HTTPException):

    def __init__(
        self,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_id='INTERNAL_SERVER_ERROR',
        message='Ocorreu um erro interno no servidor',
        detail=''
    ) -> None:
        self.status_code = status_code
        self.error_id = error_id
        self.message = message
        self.detail = detail


class UnprocessableEntityException(ApiBaseException):

    def __init__(
        self,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_id='UNPROCESSABLE_ENTITY',
        message='Ocorreu um problema ao processar a entidade',
        detail=''
    ) -> None:
        super().__init__(status_code, error_id, message, detail)


class InvalidEmailException(ApiBaseException):

    def __init__(
        self,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_id='INVALID_EMAIL',
        message='Email inválido',
        detail=''
    ) -> None:
        super().__init__(status_code, error_id, message, detail)


class UsernameConflictException(ApiBaseException):

    def __init__(
        self,
        status_code=status.HTTP_409_CONFLICT,
        error_id='USERNAME_ALREADY_EXISTS',
        message='O nome de usuário já existe no sistema',
        detail=''
    ) -> None:
        super().__init__(status_code, error_id, message, detail)


class EmailConflictException(ApiBaseException):

    def __init__(
        self,
        status_code=status.HTTP_409_CONFLICT,
        error_id='EMAIL_ALREADY_EXISTS',
        message='O e-mail já existe no sistema',
        detail=''
    ) -> None:
        super().__init__(status_code, error_id, message, detail)


def generic_exception_handler(_: Request, exception: Exception):
    return api_base_exception_handler(_, ApiBaseException())


def api_base_exception_handler(_: Request, exception: ApiBaseException):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            'status_code': exception.status_code,
            'error_id': exception.error_id,
            'message': exception.message,
            'detail': exception.detail,
        }
    )

