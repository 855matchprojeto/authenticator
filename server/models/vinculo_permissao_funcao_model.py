from sqlalchemy import Column, BigInteger, ForeignKey
from server.models import AuthenticatorBase
from server.configuration import db
from sqlalchemy.orm import relationship


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

    funcao = relationship('Funcao', back_populates='vinculos_permissao_funcao')
    permissao = relationship('Permissao', back_populates='vinculos_permissao_funcao')

