from sqlalchemy import Column, BigInteger, ForeignKey
from server.models import AuthenticatorBase
from server.configuration import db
from server.models.funcao_model import Funcao
from server.models.usuario_model import Usuario
from sqlalchemy.orm import relationship, backref


class VinculoUsuarioFuncao(db.Base, AuthenticatorBase):

    """
        Vínculos NXN de usuários com suas funções
    """

    def __init__(self, **kwargs):
        super(VinculoUsuarioFuncao, self).__init__(**kwargs)

    __tablename__ = "tb_vinculo_usuario_funcao"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    id_usuario = Column(BigInteger, ForeignKey("tb_usuario.id"))
    id_funcao = Column(BigInteger, ForeignKey("tb_funcao.id"))

    usuario = relationship(Usuario, backref=backref('tb_vinculo_usuario_funcao', cascade='all, delete-orphan'))
    funcao = relationship(Funcao, backref=backref('tb_vinculo_usuario_funcao', cascade='all, delete-orphan'))

