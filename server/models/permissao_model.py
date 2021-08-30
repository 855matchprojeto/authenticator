from sqlalchemy import Column, BigInteger, String
from server.models import AuthenticatorBase
from server.configuration import db
from sqlalchemy.orm import relationship


class Permissao(db.Base, AuthenticatorBase):

    def __init__(self, **kwargs):
        super(Permissao, self).__init__(**kwargs)

    __tablename__ = "tb_permissao"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nome = Column(String(), nullable=False, unique=True)
    descricao = Column(String(), nullable=False, unique=True)

    funcoes = relationship(
        'Funcao',
        primaryjoin=(
            'VinculoPermissaoFuncao.id_permissao == Permissao.id'
        ),
        secondary='tb_vinculo_permissao_funcao'
    )

