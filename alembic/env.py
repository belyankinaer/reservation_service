from alembic import context
from sqlalchemy import engine_from_config, pool

from app.constants import DATABASE_URL_NO_ASYNC
from app.models import Base

config = context.config
target_metadata = Base.metadata

config.set_main_option('sqlalchemy.url', DATABASE_URL_NO_ASYNC)

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    pass
else:
    run_migrations_online()