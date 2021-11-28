# Universidade Estadual de Campinas
# Instituto da Computação

# Disciplina: MC855-2s2021

## Professor e Assistente

| Nome                     | Email                   |
| ------------------------ | ------------------------|
| Professora Juliana Borin | jufborin@unicamp.br     |
| Assistente Paulo Kussler | paulo.kussler@gmail.com |


## Equipe

| Nome               | RA               | Email                  | ID Git                |
| ------------------ | ---------------- | ---------------------- |---------------------- |
| Gustavo Henrique Libraiz Teixeira                   | 198537                 | g198537@dac.unicamp.br                     |   nugnu                    |
| Lucas Henrique Machado Domingues                   | 182557                 | l182557@dac.unicamp.br                    |   lhmdomingues                   ||                    |                  |                        |                       |
| Matheus Vicente Mazon                   | 203609                | m203609@dac.unicamp.br                     |   matheusmazon                    |
| Pietro Pugliesi                   | 185921               | p185921@dac.unicamp.br                     |   pietro1704                   |
| Caio Lucas Silveira de Sousa                  | 165461                | c165461@dac.unicamp.br                     |   caiolucasw                    |
| Thomas Gomes Ferreira                  | 224919                | t224919@dac.unicamp.br                     |   Desnord                   |

## Específico sobre esse repositório: 
Esse repositório faz parte do projetos da plataforma de Match de Projetos desenvolvido no 2s/2021 para a disciplina MC-855 na Unicamp (https://github.com/orgs/855matchprojeto/repositories). Neste repositório se encontra a implementação do microsserviço de autenticação dos usuários (criação de usuário, login, etc) para o projeto

## Descrição do projeto:
Nosso projeto é uma plataforma em que os usuários cadastrados (da Unicamp, vide políticas de acesso), alunos ou professores, podem cadastrar projetos (com título, imagem, descrição, cursos e áreas envolvidas), e disponibilizar na plataforma para outro usuário "dar match", isso é, mostrar interesse. O usuário também tem, na sua página "Home", uma lista de projetos disponíveis que podem ser do seu interesse.

Desse modo, ocorre a conexão entre as pessoas interessadas no projeto, tornando o processo de divulgação do projeto mais centralizado e simplificado.

## Prints das telas com descrição das funcionalidades. 
<img width="883" alt="Captura de Tela 2021-11-25 às 11 30 52" src="https://user-images.githubusercontent.com/45739756/143462405-238cd087-ae71-44a5-99f8-b36f93cffae6.png">

### página de detalhes do projeto, seja ele criado pelo usuário atual ou por outro, onde o usuário pode mostrar interesse no projeto

<img width="892" alt="Captura de Tela 2021-11-25 às 11 30 46" src="https://user-images.githubusercontent.com/45739756/143462565-9e591210-bd22-48cb-875c-32a5907d1603.png">

### página de perfil do usuário atual, permitindo edição dos dados

<img width="939" alt="Captura de Tela 2021-11-25 às 11 30 38" src="https://user-images.githubusercontent.com/45739756/143462637-cb215f5c-97a3-41ec-beca-17b1d397ee9d.png">

### página de edição de projeto criado pelo usuário atual


## Tecnologias, ferramentas, dependências, versões. etc. 

### Visão geral da arquitetura

A arquitetura do back-end será definida em microsserviços. Ao contrário de uma arquitetura convencional monolítica, a aplicação em microsserviços é desmembrada em partes menores e independentes entre si.

Ao fazer o login pelo autenticador, o usuário receberá um token de acesso, com um tempo de expiração bem definido. No token, estarão disponíveis informações como 'username', 'email' e as funções desse usuário no sistema. Ao se comunicar com outros microsserviços, será necessário um header de autenticação, contendo esse token. Cada microsserviço será responsável por descriptografar e validar o token. 

Apesar do microsserviço de autenticação ser responsável pela criação de usuários e suas funções, cada microsserviço implementará seu próprio sistema de permissões, com base nas funções do usuário que fez a requisição. Note que as funções do usuário estarão disponíveis no token de acesso decodificado.

### Descrição do authenticator

O microsserviço de autenticação é responsável pela implementação do serviço de identificação de usuários. Além disso, são definidos tabelas para o banco de dados, tais como usuário, função e vínculo de usuários com funções. Como supracitado, o autenticador também definirá tabelas de permissões, específicas para esse microsserviço.

Features Implementadas:

- Criação de usuários apenas com o domínio da UNICAMP
- Autenticação baseada em tokens JWT
- Envio de e-mail para verificação de usuário
- Verificação de e-mail utilizando token enviado pelo usuário ao clicar no link do e-mail
- Testes unitários e de integração

### FAST-API

Os microsserviços serão implementados utilizando o framework web FAST-API. É um framework baseado no módulo de type-hints do python. A partir dos type-hints, o framework realiza a documentação de maneira automática, definindo inputs e outputs de um endpoint. 

O FAST-API implementa a especificação ASGI (Asynchronous Server Gateway Interface), que provê um padrão assíncrono (e também um padrão síncrono) para implementação de aplicativos em python. Nesse projeto, utilizaremos a funcionalidade assíncrona do FAST-API em nosso favor, principalmente ao requisitar o banco de dados.

### LINK DA API ATUAL

https://authenticator-match-projetos.herokuapp.com/docs

### SQL-Alchemy

O SQL-Alchemy é uma biblioteca em python, com o objetivo de facilitar a comunicação entre programas e python com um banco de dados relacional. 

Nesse projeto, utilizaremos o ORM (Object Relational Mapper) do SQL-Alchemy, conectando a um banco de dados PostgreSQL. Um ORM é uma ferramenta capaz de traduzir classes do python em tabelas. Além disso, funções em python podem representar queries e statements.

Além disso, o ORM provê uma flexibilidade de tecnologias de banco de dados. A tradução, citada anteriormente, é realizada de maneira similar nos bancos de dados que o SQL-Alchemy implementa. Por exemplo, se houver necessidade de alterar a tecnologia de banco de dados PostgreSQL vigente para outra, como MySQL, não haverá muitos problemas.

### Alembic

O Alembic é uma ferramenta de migração de dados, que funciona a partir da 'engine' disponível no SQL-Alchemy. O Alembic se conecta à um banco de dados e define um versionamento 'alembic_version'. A partir do 'metadata' do banco de dados criado no projeto, o Alembic é capaz de verificar se foram implementadas alterações nas classes que definem os modelos do banco de dados. Caso requisitado pelo programador, o Alembic pode gerar um script de revisão, com as alterações necessárias no banco de dados. Ao executar esse script, o banco de dados é atualizado.

Podemos citar algumas funcionalidades importantes no CLI do Alembic:

- alembic init: Gera os templates necessários para o funcionamento do Alembic. Algumas informações devem ser preenchidas no template, como a conexão com o banco de dados
- alembic revision --autogenerate: Gera o arquivo de revisão explicado anteriormente. Note que a revisão pode não ser perfeita. Sempre verifique os scripts de revisão gerados e os corrige se necessário.
- alembic upgrade head: Atualiza o banco de dados para a última versão definida pelo Alembic.
- alembic upgrade {revision}: Atualiza o banco de dados para a versão definida em 'revision'. Esse campo está disponível nos scripts de revisão gerados, na variável 'revision'.
- alembic downgrade -1: Desfaz a última alteração definida pelo alembic
- alembic downgrade {revision}: Desfaz as últimas alterações definidas pelo alembic, até que se retorna à versão definida por {revision}.

## Ambientes

## Como colocar no ar, como testar, etc
Acesso ao site pelo link: https://match-projetos.herokuapp.com/
OBS: o primeiro acesso pode demorar um pouco até o Heroku responder. Favor continuar atualizando a página

## Como acessar, quem pode se cadastrar(regras de acessos), etc.
Acesso com usuário com nome de usuário "admin" e senha "admin123", ou realizar cadastro próprio. A regra de acesso é que o email cadastrado no usuário deve ser de domínio da Unicamp, isto é, de final "unicamp.br"


# Notas específicas sobre o autenthicator
## Estrutura do código

### configuration

Essa pasta é responsável por definir módulos responsáveis por: 

- Conexão com o banco de dados assíncrono
- Variáveis de ambiente
- Exceções customizadas
- Constantes
- Logging

### controllers

Essa pasta é responsável por definir a primeira camada de acesso aos endpoints. Nela são definidos:

- Rotas
- Paths dos endpoitns
- Dependências
- Decorator para tratar exceções com rollback do banco de dados

### services

Define a lógica dos endpoints, abstraindo o acesso ao banco de dados, que é efetuado pelos módulos definidos na pastas repository

### repository

Define os métodos que atuam diretamente com banco de dados

### dependencies

Define as injeções de dependência utilizadas pelos controllers. Pode-se citar:

- Dependências de segurança, como o Form do OAuth2
- Sessão do banco de dados assícrono

### models

Define as classes que representam o banco de dados, suas tabelas e campos

### schemas

Essa classe é necessária para definir inputs e outputs de endpoints, permitindo a documentação automática do FAST-API.
