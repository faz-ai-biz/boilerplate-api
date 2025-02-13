from alembic import context
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from sqlalchemy import engine_from_config
from src.core.config import settings
from src.db.models import Base
import os
import sys

config = context.config
fileConfig(config.config_file_name)

# ✅ Read database URL from environment
DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL environment variable is not set!")

target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
