from sqlalchemy import Column, BigInteger, String
from server.models import AuthenticatorBase
from server.configuration import db
from sqlalchemy.orm import relationship


class Funcao(db.Base, AuthenticatorBase):

    def __init__(self, **kwargs):
        super(Funcao, self).__init__(**kwargs)

    __tablename__ = "tb_funcao"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nome = Column(String(), nullable=False, unique=True)
    descricao = Column(String(), nullable=False, unique=True)

    vinculos_usuario_funcao = relationship(
        'VinculoUsuarioFuncao',
        back_populates='funcao'
    )

    vinculos_permissao_funcao = relationship(
        'VinculoPermissaoFuncao',
        back_populates='funcao'
    )

