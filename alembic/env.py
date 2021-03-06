from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from server.configuration.db import Base
from sqlalchemy import create_engine
from server.configuration.environment import MigrationEnvironment


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


from server.models import (
    funcao_model,
    permissao_model,
    usuario_model,
    vinculo_usuario_funcao_model,
    vinculo_permissao_funcao_model
)


target_metadata = Base.metadata


def get_url():
    environment = MigrationEnvironment()
    return environment.get_db_conn_default(
        db_host=environment.MIGRATION_DB_HOST,
        db_name=environment.MIGRATION_DB_NAME,
        db_port=environment.MIGRATION_DB_PORT,
        db_pass=environment.MIGRATION_DB_PASS,
        db_user=environment.MIGRATION_DB_USER
    )


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = create_engine(
        get_url(),
        poolclass=pool.NullPool,
        pool_pre_ping=True
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
