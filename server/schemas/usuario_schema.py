from server.schemas import AuthenticatorModelInput, AuthenticatorModelOutput
from uuid import UUID as GUID
import sqlalchemy
from pydantic import Field
from datetime import datetime


class UsuarioInput(AuthenticatorModelInput):

    nome: str
    username: str
    password: str
    email: str

    def convert_to_dict(self):
        return self.dict()

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class UsuarioOutput(AuthenticatorModelOutput):

    guid: GUID = Field(None)
    nome: str = Field(None)
    username: str = Field(None)
    email: str = Field(None)
    email_verificado: bool = Field(None)
    created_at: datetime = Field(None)
    updated_at: datetime = Field(None)

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

