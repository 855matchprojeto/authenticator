import uuid
from uuid import UUID as GUID

import sqlalchemy
from pydantic import Field
from sqlalchemy import Column, BigInteger, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from server.model import AuthenticatorBase, AuthenticatorModelInput, \
    AuthenticatorModelOutput
from server.configuration import db


# DB


class Usuario(db.Base, AuthenticatorBase):

    def __init__(self, **kwargs):
        super(Usuario, self).__init__(**kwargs)

    __tablename__ = "tb_usuario"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guid = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    nome = Column(String())
    username = Column(String(), unique=True, nullable=False)
    hashed_password = Column(String(), nullable=False)
    email = Column(String(), unique=True, nullable=False)
    email_verificado = Column(Boolean(), default=False)


# Schemas


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

