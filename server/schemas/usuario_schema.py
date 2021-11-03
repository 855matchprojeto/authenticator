from server.schemas import AuthenticatorModelInput, AuthenticatorModelOutput
from pydantic import Field, BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
from uuid import UUID as GUID


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

    guid: GUID
    nome: str = Field(None, example='Teste')
    username: str = Field(None, example='username')
    email: EmailStr = Field(None, example="teste@unicamp.br")
    email_verificado: bool = Field(None)
    created_at: datetime = Field(None)
    updated_at: datetime = Field(None)

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class UsuarioPublishInput(BaseModel):

    guid: GUID
    nome: str = Field(None, example='Teste')
    username: str = Field(None, example='username')
    email: EmailStr = Field(None, example="teste@unicamp.br")
    email_verificado: bool = Field(None)
    created_at: datetime = Field(None)

    def convert_to_dict(self):
        _dict = self.dict()
        _dict['guid'] = str(_dict['guid'])
        _dict['created_at'] = str(_dict['created_at'])
        return _dict


class CurrentUserToken(BaseModel):

    name: str
    username: str
    guid: str
    email: EmailStr
    roles: List[int]
    permissions: Optional[List[str]]


class CurrentUserOutput(BaseModel):

    name: str = Field(example='Teste')
    username: str = Field(example='username')
    guid: str = Field(example='78628c23-aae3-4d58-84a9-0c8d7ea63672')
    email: EmailStr = Field(example="teste@unicamp.br")

