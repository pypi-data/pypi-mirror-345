from typing import TYPE_CHECKING

from archipy.adapters.base.sqlalchemy.session_manager_registry import SessionManagerRegistry
from archipy.helpers.metaclasses.singleton import Singleton

if TYPE_CHECKING:
    from archipy.adapters.base.sqlalchemy.session_manager_ports import AsyncSessionManagerPort, SessionManagerPort


class SqliteSessionManagerRegistry(SessionManagerRegistry, metaclass=Singleton):
    """Registry for SQLite SQLAlchemy session managers.

    This registry provides a centralized access point for both synchronous and
    asynchronous SQLite session managers, implementing the Service Locator pattern.
    It lazily initializes the appropriate session manager when first requested.

    The registry maintains singleton instances of:
    - A synchronous session manager (SqliteSQlAlchemySessionManager)
    - An asynchronous session manager (AsyncSqliteSQlAlchemySessionManager)
    """

    _sync_instance: "SessionManagerPort | None" = None
    _async_instance: "AsyncSessionManagerPort | None" = None

    @classmethod
    def get_sync_manager(cls) -> "SessionManagerPort":
        """Get the synchronous SQLite session manager instance.

        Lazily initializes a default SqliteSQlAlchemySessionManager if none has been set.

        Returns:
            SessionManagerPort: The registered synchronous session manager
        """
        if cls._sync_instance is None:
            from archipy.adapters.sqlite.sqlalchemy.session_managers import SqliteSQlAlchemySessionManager

            cls._sync_instance = SqliteSQlAlchemySessionManager()
        return cls._sync_instance

    @classmethod
    def set_sync_manager(cls, manager: "SessionManagerPort") -> None:
        """Set a custom synchronous session manager.

        Args:
            manager: An instance implementing SessionManagerPort
        """
        cls._sync_instance = manager

    @classmethod
    def get_async_manager(cls) -> "AsyncSessionManagerPort":
        """Get the asynchronous SQLite session manager instance.

        Lazily initializes a default AsyncSqliteSQlAlchemySessionManager if none has been set.

        Returns:
            AsyncSessionManagerPort: The registered asynchronous session manager
        """
        if cls._async_instance is None:
            from archipy.adapters.sqlite.sqlalchemy.session_managers import AsyncSqliteSQlAlchemySessionManager

            cls._async_instance = AsyncSqliteSQlAlchemySessionManager()
        return cls._async_instance

    @classmethod
    def set_async_manager(cls, manager: "AsyncSessionManagerPort") -> None:
        """Set a custom asynchronous session manager.

        Args:
            manager: An instance implementing AsyncSessionManagerPort
        """
        cls._async_instance = manager

    @classmethod
    def reset(cls) -> None:
        """Reset the registry to its initial state.

        This method clears both registered managers, useful for testing.
        """
        cls._sync_instance = None
        cls._async_instance = None
