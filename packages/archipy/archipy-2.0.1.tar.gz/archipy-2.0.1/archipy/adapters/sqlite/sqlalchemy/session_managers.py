from typing import override

from sqlalchemy import URL

from archipy.adapters.base.sqlalchemy.session_managers import (
    AsyncBaseSQLAlchemySessionManager,
    BaseSQLAlchemySessionManager,
)
from archipy.configs.base_config import BaseConfig
from archipy.configs.config_template import SqliteSQLAlchemyConfig
from archipy.helpers.metaclasses.singleton import Singleton


class SqliteSQlAlchemySessionManager(BaseSQLAlchemySessionManager, metaclass=Singleton):
    """Synchronous SQLAlchemy session manager for SQLite.

    Inherits from BaseSQLAlchemySessionManager to provide SQLite-specific session
    management, optimized for in-memory testing with thread-safe connections.

    Args:
        orm_config: SQLite-specific configuration. If None, uses global config.
    """

    def __init__(self, orm_config: SqliteSQLAlchemyConfig | None = None) -> None:
        """Initialize the SQLite session manager.

        Args:
            orm_config: SQLite-specific configuration. If None, uses global config.
        """
        configs = BaseConfig.global_config().SQLITE_SQLALCHEMY if orm_config is None else orm_config
        super().__init__(configs)

    @override
    def _expected_config_type(self) -> type[SqliteSQLAlchemyConfig]:
        """Return the expected configuration type for SQLite.

        Returns:
            The SqliteSQLAlchemyConfig class.
        """
        return SqliteSQLAlchemyConfig

    @override
    def _create_url(self, configs: SqliteSQLAlchemyConfig) -> URL:
        """Create a SQLite connection URL for in-memory database.

        Args:
            configs: SQLite configuration.

        Returns:
            A SQLAlchemy URL object for SQLite.
        """
        return URL.create(
            drivername=configs.DRIVER_NAME,
            database=configs.DATABASE or ":memory:",  # Default to in-memory
        )

    @override
    def _get_connect_args(self) -> dict:
        """Return SQLite-specific connection arguments.

        Returns:
            A dictionary with thread safety settings for SQLite.
        """
        return {"check_same_thread": False}


class AsyncSqliteSQlAlchemySessionManager(AsyncBaseSQLAlchemySessionManager, metaclass=Singleton):
    """Asynchronous SQLAlchemy session manager for SQLite.

    Inherits from AsyncBaseSQLAlchemySessionManager to provide async SQLite-specific
    session management, optimized for in-memory testing.

    Args:
        orm_config: SQLite-specific configuration. If None, uses global config.
    """

    def __init__(self, orm_config: SqliteSQLAlchemyConfig | None = None) -> None:
        """Initialize the async SQLite session manager.

        Args:
            orm_config: SQLite-specific configuration. If None, uses global config.
        """
        configs = BaseConfig.global_config().SQLITE_SQLALCHEMY if orm_config is None else orm_config
        super().__init__(configs)

    @override
    def _expected_config_type(self) -> type[SqliteSQLAlchemyConfig]:
        """Return the expected configuration type for SQLite.

        Returns:
            The SqliteSQLAlchemyConfig class.
        """
        return SqliteSQLAlchemyConfig

    @override
    def _create_url(self, configs: SqliteSQLAlchemyConfig) -> URL:
        """Create an async SQLite connection URL for in-memory database.

        Args:
            configs: SQLite configuration.

        Returns:
            A SQLAlchemy URL object for SQLite.
        """
        return URL.create(
            drivername=configs.DRIVER_NAME,
            database=configs.DATABASE or ":memory:",  # Default to in-memory
        )
