"""
Alembic environment configuration for Tracerfy Backend
"""

from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy import create_engine
from alembic import context
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.db.base import Base
from app.models import *  # Import all models

# Import all models to ensure they are registered with Base.metadata
from app.models.user import User
from app.models.api_key import APIKey

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_database_url():
    """Get database URL from settings"""
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with a connection"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = create_engine(
        configuration["sqlalchemy.url"],
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


def include_object(object, name, type_, reflected, compare_to):
    """
    Determine whether to include a specific object in migrations.
    This helps control what gets included in auto-generated migrations.
    """
    # Exclude certain tables or objects if needed
    if type_ == "table" and name in ["alembic_version"]:
        return False
    
    # Exclude temporary tables
    if type_ == "table" and name.startswith("temp_"):
        return False
    
    # Exclude test tables in production
    if settings.ENVIRONMENT == "production" and name.startswith("test_"):
        return False
    
    return True


def render_item(type_, obj, autogen_context):
    """
    Custom rendering for migration items.
    This allows customizing how certain database objects are rendered.
    """
    # Custom rendering for specific column types if needed
    if type_ == "type" and hasattr(obj, "__visit_name__"):
        if obj.__visit_name__ == "uuid":
            return "UUID(as_uuid=True)"
        elif obj.__visit_name__ == "json":
            return "JSON"
        elif obj.__visit_name__ == "jsonb":
            return "JSONB"
    
    # Default rendering
    return False


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
