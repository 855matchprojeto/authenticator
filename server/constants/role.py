"""
    Define as funções dos usuários do sistema.
    É especialmente útil para definir os scopes do token de acesso
"""


class Role:

    # DEFAULT = {
    #     "name": "DEFAULT",
    #     "description": "Usuário padrão do sistema, que ainda não foi verificado"
    # }
    # POR ENQUANTO NAO TER FUNCAO EQUIVALE A USER DEFAULT

    ALUNO = {
        "name": "ALUNO",
        "description": "Usuário verificado como um aluno"
    }

    PROFESSOR = {
        "name": "PROFESSOR",
        "description": "Usuário verificado como um professor"
    }

    ADMIN = {
        "name": "ADMIN",
        "description": "Usuário com acesso administrativo"
    }

    @staticmethod
    def get_all_roles_list():
        return [
            # Role.DEFAULT,
            Role.ALUNO,
            Role.PROFESSOR,
            Role.ADMIN
        ]

    @staticmethod
    def get_all_roles_dict():
        all_roles_dict = {}
        for role_dict in Role.get_all_roles_list():
            all_roles_dict.update({role_dict['name']: role_dict['description']})
        print(all_roles_dict)
        return all_roles_dict


