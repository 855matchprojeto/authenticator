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

DATABASE_URL = 'postgres://xojmqlwdxfynpb:8a0a8cc1689c0e066ac33dc6fca194bf610cc764d6f71c87e6318dd49c82fa52@ec2-18-209-153-180.compute-1.amazonaws.com:5432/dcbi94kke45ffj'
DB_CONN_ASYNC = re.sub(r'\bpostgres://\b', "postgresql+asyncpg://", str(DATABASE_URL), count=1)
DB_CONN = re.sub(r'\bpostgres://\b', "postgresql://", str(DATABASE_URL), count=1)

# Configurações do servidor

ENVIRONMENT = os.getenv('ENVIRONMENT') or 'DEV'
HOST = os.getenv('HOST') or 'localhost'
PORT = os.getenv('PORT') or 8083
