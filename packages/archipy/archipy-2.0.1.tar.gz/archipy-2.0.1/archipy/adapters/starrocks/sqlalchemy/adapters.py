from typing import override

from archipy.adapters.base.sqlalchemy.adapters import AsyncBaseSQLAlchemyAdapter, BaseSQLAlchemyAdapter
from archipy.adapters.starrocks.sqlalchemy.session_managers import (
    AsyncStarrocksSQlAlchemySessionManager,
    StarrocksSQlAlchemySessionManager,
)
from archipy.configs.base_config import BaseConfig
from archipy.configs.config_template import StarrocksSQLAlchemyConfig


class StarrocksSQLAlchemyAdapter(BaseSQLAlchemyAdapter):
    """Synchronous SQLAlchemy adapter for Starrocks.

    Inherits from BaseSQLAlchemyAdapter to provide Starrocks-specific session management
    and database operations.

    Args:
        orm_config: Starrocks-specific configuration. If None, uses global config.
    """

    def __init__(self, orm_config: StarrocksSQLAlchemyConfig | None = None) -> None:
        """Initialize the Starrocks adapter with a session manager.

        Args:
            orm_config: Starrocks-specific configuration. If None, uses global config.
        """
        configs = BaseConfig.global_config().STARROCKS_SQLALCHEMY if orm_config is None else orm_config
        super().__init__(configs)

    @override
    def _create_session_manager(self, configs: StarrocksSQLAlchemyConfig) -> StarrocksSQlAlchemySessionManager:
        """Create a Starrocks-specific session manager.

        Args:
            configs: Starrocks configuration.

        Returns:
            A Starrocks session manager instance.
        """
        return StarrocksSQlAlchemySessionManager(configs)


class AsyncStarrocksSQLAlchemyAdapter(AsyncBaseSQLAlchemyAdapter):
    """Asynchronous SQLAlchemy adapter for Starrocks.

    Inherits from AsyncBaseSQLAlchemyAdapter to provide async Starrocks-specific session
    management and database operations.

    Args:
        orm_config: Starrocks-specific configuration. If None, uses global config.
    """

    def __init__(self, orm_config: StarrocksSQLAlchemyConfig | None = None) -> None:
        """Initialize the async Starrocks adapter with a session manager.

        Args:
            orm_config: Starrocks-specific configuration. If None, uses global config.
        """
        configs = BaseConfig.global_config().STARROCKS_SQLALCHEMY if orm_config is None else orm_config
        super().__init__(configs)

    @override
    def _create_async_session_manager(
        self,
        configs: StarrocksSQLAlchemyConfig,
    ) -> AsyncStarrocksSQlAlchemySessionManager:
        """Create an async Starrocks-specific session manager.

        Args:
            configs: Starrocks configuration.

        Returns:
            An async Starrocks session manager instance.
        """
        return AsyncStarrocksSQlAlchemySessionManager(configs)
