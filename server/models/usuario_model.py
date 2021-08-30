import uuid
from sqlalchemy import Column, BigInteger, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from server.models import AuthenticatorBase
from server.configuration import db
from sqlalchemy.orm import relationship


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

    funcoes = relationship(
        "Funcao",
        primaryjoin=(
          'VinculoUsuarioFuncao.id_usuario == Usuario.id'
        ),
        secondary='tb_vinculo_usuario_funcao'
    )

