import os

# Configurações do banco de dados

DB_HOST = os.getenv('DB_HOST') or 'localhost'
DB_USER = os.getenv('DB_USER') or 'postgres'
DB_PASS = os.getenv('DB_PASS') or '1234'
DB_NAME = os.getenv('DB_NAME') or 'db_mc855_authenticator'
DB_PORT = os.getenv('DB_PORT') or '5438'
DB_ECHO = os.getenv('DB_ECHO') or True
DB_POOL_SIZE = os.getenv('DB_POOL_SIZE') or 80
DB_MAX_OVERFLOW = os.getenv('DB_MAX_OVERFLOW') or 10
DB_POOL_PRE_PING = os.getenv('DB_POOL_PRE_PING') or True
DB_CONN = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Configurações do servidor

ENVIRONMENT = os.getenv('ENVIRONMENT') or 'DEV'
HOST = os.getenv('HOST') or 'localhost'
PORT = os.getenv('PORT') or 8081
