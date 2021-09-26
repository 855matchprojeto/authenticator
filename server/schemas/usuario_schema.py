from server.schemas import AuthenticatorModelInput, AuthenticatorModelOutput
from pydantic import Field, BaseModel, EmailStr
from datetime import datetime
from typing import List


class UsuarioInput(AuthenticatorModelInput):

    nome: str = Field(example='Teste')
    username: str = Field(example='username')
    password: str = Field(example='password')
    email: EmailStr = Field(example="teste@unicamp.br")

    def convert_to_dict(self):
        return self.dict()

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class UsuarioOutput(AuthenticatorModelOutput):

    nome: str = Field(None, example='Teste')
    username: str = Field(None, example='username')
    email: EmailStr = Field(None, example="teste@unicamp.br")
    email_verificado: bool = Field(None)
    created_at: datetime = Field(None)
    updated_at: datetime = Field(None)

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class CurrentUser(BaseModel):

    name: str
    username: str
    guid: str
    email: EmailStr
    roles: List[int]
    permissions: List[str]

