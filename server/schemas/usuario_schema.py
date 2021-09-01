from server.schemas import AuthenticatorModelInput, AuthenticatorModelOutput
from uuid import UUID as GUID
import sqlalchemy
from pydantic import Field, BaseModel, EmailStr
from datetime import datetime
from typing import List
from server.models.permissao_model import Permissao


class UsuarioInput(AuthenticatorModelInput):

    nome: str
    username: str
    password: str
    email: EmailStr

    def convert_to_dict(self):
        return self.dict()

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class UsuarioOutput(AuthenticatorModelOutput):

    nome: str = Field(None)
    username: str = Field(None)
    email: EmailStr = Field(None)
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

