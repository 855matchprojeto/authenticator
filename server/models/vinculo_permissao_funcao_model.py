from sqlalchemy import Column, BigInteger, ForeignKey
from server.models import AuthenticatorBase
from server.configuration import db
from sqlalchemy.orm import relationship, backref
from server.models.funcao_model import Funcao
from server.models.permissao_model import Permissao


class VinculoPermissaoFuncao(db.Base, AuthenticatorBase):

    """
        Vínculos NXN de permissões com funções de usuário
    """

    def __init__(self, **kwargs):
        super(VinculoPermissaoFuncao, self).__init__(**kwargs)

    __tablename__ = "tb_vinculo_permissao_funcao"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    id_permissao = Column(BigInteger, ForeignKey("tb_permissao.id"))
    id_funcao = Column(BigInteger, ForeignKey("tb_funcao.id"))

    permissao = relationship(Permissao, backref=backref('tb_vinculo_permissao_funcao', cascade='all, delete-orphan'))
    funcao = relationship(Funcao, backref=backref('tb_vinculo_permissao_funcao', cascade='all, delete-orphan'))

