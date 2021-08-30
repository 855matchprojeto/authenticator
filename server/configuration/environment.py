import os
import re

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

DATABASE_URL = os.getenv('DATABASE_URL')
DB_CONN_ASYNC = re.sub(r'\bpostgres://\b', "postgresql+asyncpg://", str(DATABASE_URL), count=1)
DB_CONN = re.sub(r'\bpostgres://\b', "postgresql://", str(DATABASE_URL), count=1)

# Configurações do servidor

ENVIRONMENT = os.getenv('ENVIRONMENT') or 'DEV'
HOST = os.getenv('HOST') or 'localhost'
PORT = int(os.getenv('PORT')) if os.getenv('PORT') else 8080

ACCESS_TOKEN_EXPIRE_DELTA_IN_SECONDS = int(os.getenv('ACCESS_TOKEN_EXPIRE_DELTA_IN_SECONDS') or '1800')
EMAIL_TOKEN_EXPIRE_DELTA_IN_SECONDS = int(os.getenv('EMAIL_TOKEN_EXPIRE_DELTA_IN_SECONDS') or '600')
ACCESS_TOKEN_SECRET_KEY = os.getenv('ACCESS_TOKEN_SECRET_KEY')
ACCESS_TOKEN_ALGORITHM = os.getenv('ACCESS_TOKEN_ALGORITHM')

