from typing import override

from sqlalchemy import URL

from archipy.adapters.base.sqlalchemy.session_managers import (
    AsyncBaseSQLAlchemySessionManager,
    BaseSQLAlchemySessionManager,
)
from archipy.configs.base_config import BaseConfig
from archipy.configs.config_template import PostgresSQLAlchemyConfig
from archipy.helpers.metaclasses.singleton import Singleton


class PostgresSQlAlchemySessionManager(BaseSQLAlchemySessionManager, metaclass=Singleton):
    """Synchronous SQLAlchemy session manager for PostgreSQL.

    Inherits from BaseSQLAlchemySessionManager to provide PostgreSQL-specific session
    management, including connection URL creation and engine configuration.

    Args:
        orm_config: PostgreSQL-specific configuration. If None, uses global config.
    """

    def __init__(self, orm_config: PostgresSQLAlchemyConfig | None = None) -> None:
        """Initialize the PostgreSQL session manager.

        Args:
            orm_config: PostgreSQL-specific configuration. If None, uses global config.
        """
        configs = BaseConfig.global_config().POSTGRES_SQLALCHEMY if orm_config is None else orm_config
        super().__init__(configs)

    @override
    def _expected_config_type(self) -> type[PostgresSQLAlchemyConfig]:
        """Return the expected configuration type for PostgreSQL.

        Returns:
            The PostgresSQLAlchemyConfig class.
        """
        return PostgresSQLAlchemyConfig

    @override
    def _create_url(self, configs: PostgresSQLAlchemyConfig) -> URL:
        """Create a PostgreSQL connection URL.

        Args:
            configs: PostgreSQL configuration.

        Returns:
            A SQLAlchemy URL object for PostgreSQL.
        """
        return URL.create(
            drivername=configs.DRIVER_NAME,
            username=configs.USERNAME,
            password=configs.PASSWORD,
            host=configs.HOST,
            port=configs.PORT,
            database=configs.DATABASE,
        )


class AsyncPostgresSQlAlchemySessionManager(AsyncBaseSQLAlchemySessionManager, metaclass=Singleton):
    """Asynchronous SQLAlchemy session manager for PostgreSQL.

    Inherits from AsyncBaseSQLAlchemySessionManager to provide async PostgreSQL-specific
    session management, including connection URL creation and async engine configuration.

    Args:
        orm_config: PostgreSQL-specific configuration. If None, uses global config.
    """

    def __init__(self, orm_config: PostgresSQLAlchemyConfig | None = None) -> None:
        """Initialize the async PostgreSQL session manager.

        Args:
            orm_config: PostgreSQL-specific configuration. If None, uses global config.
        """
        configs = BaseConfig.global_config().POSTGRES_SQLALCHEMY if orm_config is None else orm_config
        super().__init__(configs)

    @override
    def _expected_config_type(self) -> type[PostgresSQLAlchemyConfig]:
        """Return the expected configuration type for PostgreSQL.

        Returns:
            The PostgresSQLAlchemyConfig class.
        """
        return PostgresSQLAlchemyConfig

    @override
    def _create_url(self, configs: PostgresSQLAlchemyConfig) -> URL:
        """Create an async PostgreSQL connection URL.

        Args:
            configs: PostgreSQL configuration.

        Returns:
            A SQLAlchemy URL object for PostgreSQL.
        """
        return URL.create(
            drivername=configs.DRIVER_NAME,
            username=configs.USERNAME,
            password=configs.PASSWORD,
            host=configs.HOST,
            port=configs.PORT,
            database=configs.DATABASE,
        )
