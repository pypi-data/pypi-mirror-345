from typing import override

from sqlalchemy import URL

from archipy.adapters.base.sqlalchemy.session_managers import (
    AsyncBaseSQLAlchemySessionManager,
    BaseSQLAlchemySessionManager,
)
from archipy.configs.base_config import BaseConfig
from archipy.configs.config_template import StarrocksSQLAlchemyConfig
from archipy.helpers.metaclasses.singleton import Singleton


class StarrocksSQlAlchemySessionManager(BaseSQLAlchemySessionManager, metaclass=Singleton):
    """Synchronous SQLAlchemy session manager for Starrocks.

    Inherits from BaseSQLAlchemySessionManager to provide Starrocks-specific session
    management, including catalog-based connection URL creation.

    Args:
        orm_config: Starrocks-specific configuration. If None, uses global config.
    """

    def __init__(self, orm_config: StarrocksSQLAlchemyConfig | None = None) -> None:
        """Initialize the Starrocks session manager.

        Args:
            orm_config: Starrocks-specific configuration. If None, uses global config.
        """
        configs = BaseConfig.global_config().STARROCKS_SQLALCHEMY if orm_config is None else orm_config
        super().__init__(configs)

    @override
    def _expected_config_type(self) -> type[StarrocksSQLAlchemyConfig]:
        """Return the expected configuration type for Starrocks.

        Returns:
            The StarrocksSQLAlchemyConfig class.
        """
        return StarrocksSQLAlchemyConfig

    @override
    def _create_url(self, configs: StarrocksSQLAlchemyConfig) -> URL:
        """Create a Starrocks connection URL with catalog and database.

        Args:
            configs: Starrocks configuration.

        Returns:
            A SQLAlchemy URL object for Starrocks.
        """
        return URL.create(
            drivername=configs.DRIVER_NAME,
            username=configs.USERNAME,
            password=configs.PASSWORD,
            host=configs.HOST,
            port=configs.PORT,
            database=f"{configs.CATALOG}.{configs.DATABASE}",
        )


class AsyncStarrocksSQlAlchemySessionManager(AsyncBaseSQLAlchemySessionManager, metaclass=Singleton):
    """Asynchronous SQLAlchemy session manager for Starrocks.

    Inherits from AsyncBaseSQLAlchemySessionManager to provide async Starrocks-specific
    session management, including catalog-based connection URL creation.

    Args:
        orm_config: Starrocks-specific configuration. If None, uses global config.
    """

    def __init__(self, orm_config: StarrocksSQLAlchemyConfig | None = None) -> None:
        """Initialize the async Starrocks session manager.

        Args:
            orm_config: Starrocks-specific configuration. If None, uses global config.
        """
        configs = BaseConfig.global_config().STARROCKS_SQLALCHEMY if orm_config is None else orm_config
        super().__init__(configs)

    @override
    def _expected_config_type(self) -> type[StarrocksSQLAlchemyConfig]:
        """Return the expected configuration type for Starrocks.

        Returns:
            The StarrocksSQLAlchemyConfig class.
        """
        return StarrocksSQLAlchemyConfig

    @override
    def _create_url(self, configs: StarrocksSQLAlchemyConfig) -> URL:
        """Create an async Starrocks connection URL with catalog and database.

        Args:
            configs: Starrocks configuration.

        Returns:
            A SQLAlchemy URL object for Starrocks.
        """
        return URL.create(
            drivername=configs.DRIVER_NAME,
            username=configs.USERNAME,
            password=configs.PASSWORD,
            host=configs.HOST,
            port=configs.PORT,
            database=f"{configs.CATALOG}.{configs.DATABASE}",
        )
