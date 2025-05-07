"""SQLAlchemy atomic transaction decorators.

This module provides decorators for managing SQLAlchemy transactions with automatic commit/rollback
and support for different database types (PostgreSQL, SQLite, StarRocks).
"""

import logging
from collections.abc import Callable
from functools import partial, wraps
from typing import Any, TypeVar

from sqlalchemy.exc import OperationalError

from archipy.adapters.base.sqlalchemy.session_manager_ports import AsyncSessionManagerPort, SessionManagerPort
from archipy.adapters.base.sqlalchemy.session_manager_registry import SessionManagerRegistry
from archipy.models.errors import AbortedError, BaseError, DeadlockDetectedError, InternalError

# Constants for tracking atomic blocks and their corresponding registries
ATOMIC_BLOCK_CONFIGS = {
    "postgres": {
        "flag": "in_postgres_sqlalchemy_atomic_block",
        "registry": "archipy.adapters.postgres.sqlalchemy.session_manager_registry.PostgresSessionManagerRegistry",
    },
    "sqlite": {
        "flag": "in_sqlite_sqlalchemy_atomic_block",
        "registry": "archipy.adapters.sqlite.sqlalchemy.session_manager_registry.SqliteSessionManagerRegistry",
    },
    "starrocks": {
        "flag": "in_starrocks_sqlalchemy_atomic_block",
        "registry": "archipy.adapters.starrocks.sqlalchemy.session_manager_registry.StarrocksSessionManagerRegistry",
    },
}

# Type variables for function return types
R = TypeVar("R")


def _handle_db_exception(exception: Exception, db_type: str, func_name: str) -> None:
    """Handle database exceptions and raise appropriate errors.

    Args:
        exception (Exception): The exception to handle.
        db_type (str): The database type ("postgres", "sqlite", or "starrocks").
        func_name (str): The name of the function being executed.

    Raises:
        AbortedError: If a serialization failure is detected.
        DeadlockDetectedError: If a deadlock or database lock is detected.
        InternalError: For other unexpected errors.
    """
    logging.debug(f"Exception in {db_type} atomic block (func: {func_name}): {exception}")
    if isinstance(exception, OperationalError):
        if hasattr(exception, "orig") and exception.orig:
            sqlstate = getattr(exception.orig, "pgcode", None)
            if sqlstate == "40001":  # Serialization failure
                raise AbortedError(reason=str(exception)) from exception
            if sqlstate == "40P01":  # Deadlock detected
                raise DeadlockDetectedError() from exception
        if "database is locked" in str(exception):
            raise DeadlockDetectedError() from exception
        raise InternalError(details=str(exception)) from exception
    if isinstance(exception, BaseError):
        raise exception
    raise InternalError(details=str(exception)) from exception


def sqlalchemy_atomic_decorator(
    db_type: str,
    is_async: bool = False,
    function: Callable[..., Any] | None = None,
) -> Callable[..., Any] | partial[Callable[..., Any]]:
    """Factory for creating SQLAlchemy atomic transaction decorators.

    This decorator ensures that a function runs within a database transaction for the specified
    database type. If the function succeeds, the transaction is committed; otherwise, it is rolled back.
    Supports both synchronous and asynchronous functions.

    Args:
        db_type (str): The database type ("postgres", "sqlite", or "starrocks").
        is_async (bool): Whether the function is asynchronous. Defaults to False.
        function (Callable | None): The function to wrap. If None, returns a partial function.

    Returns:
        Callable | partial: The wrapped function or a partial function for later use.

    Raises:
        ValueError: If an invalid db_type is provided.
        AbortedError: If a serialization failure or deadlock is detected.
        DeadlockDetectedError: If an operational error occurs due to a serialization failure.
        InternalError: If any other exception occurs during execution.

    Example:
        # Synchronous PostgreSQL example
        @sqlalchemy_atomic_decorator(db_type="postgres")
        def update_user(id: int, name: str) -> None:
            # Database operations
            pass

        # Asynchronous SQLite example
        @sqlalchemy_atomic_decorator(db_type="sqlite", is_async=True)
        async def update_record(id: int, data: str) -> None:
            # Async database operations
            pass
    """
    if db_type not in ATOMIC_BLOCK_CONFIGS:
        raise ValueError(f"Invalid db_type: {db_type}. Must be one of {list(ATOMIC_BLOCK_CONFIGS.keys())}")

    atomic_flag = ATOMIC_BLOCK_CONFIGS[db_type]["flag"]

    # Dynamically import the registry class
    def get_registry() -> type[SessionManagerRegistry]:
        """Get the session manager registry for the specified database type.

        Returns:
            type[SessionManagerRegistry]: The session manager registry class.

        Raises:
            ImportError: If the registry module cannot be imported.
            AttributeError: If the registry class cannot be found.
        """
        import importlib

        module_path, class_name = ATOMIC_BLOCK_CONFIGS[db_type]["registry"].rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        """Create a transaction-aware wrapper for the given function.

        Args:
            func (Callable[..., R]): The function to wrap with transaction management.

        Returns:
            Callable[..., R]: The wrapped function that manages transactions.
        """
        if is_async:

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> R:
                """Async wrapper for managing database transactions.

                Args:
                    *args: Positional arguments to pass to the wrapped function.
                    **kwargs: Keyword arguments to pass to the wrapped function.

                Returns:
                    R: The result of the wrapped function.

                Raises:
                    AbortedError: If a serialization failure or deadlock is detected.
                    DeadlockDetectedError: If an operational error occurs due to a deadlock.
                    InternalError: If any other exception occurs during execution.
                """
                registry = get_registry()
                session_manager: AsyncSessionManagerPort = registry.get_async_manager()
                session = session_manager.get_session()
                is_nested = session.info.get(atomic_flag, False)
                if not is_nested:
                    session.info[atomic_flag] = True

                try:
                    if session.in_transaction():
                        result = await func(*args, **kwargs)
                        if not is_nested:
                            await session.commit()
                        return result
                    async with session.begin():
                        return await func(*args, **kwargs)
                except Exception as exception:
                    await session.rollback()
                    _handle_db_exception(exception, db_type, func.__name__)
                finally:
                    if not session.in_transaction():
                        await session.close()
                        await session_manager.remove_session()

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> R:
                """Synchronous wrapper for managing database transactions.

                Args:
                    *args: Positional arguments to pass to the wrapped function.
                    **kwargs: Keyword arguments to pass to the wrapped function.

                Returns:
                    R: The result of the wrapped function.

                Raises:
                    AbortedError: If a serialization failure or deadlock is detected.
                    DeadlockDetectedError: If an operational error occurs due to a deadlock.
                    InternalError: If any other exception occurs during execution.
                """
                registry = get_registry()
                session_manager: SessionManagerPort = registry.get_sync_manager()
                session = session_manager.get_session()
                is_nested = session.info.get(atomic_flag, False)
                if not is_nested:
                    session.info[atomic_flag] = True

                try:
                    if session.in_transaction():
                        result = func(*args, **kwargs)
                        if not is_nested:
                            session.commit()
                        return result
                    with session.begin():
                        return func(*args, **kwargs)
                except Exception as exception:
                    session.rollback()
                    _handle_db_exception(exception, db_type, func.__name__)
                finally:
                    if not session.in_transaction():
                        session.close()
                        session_manager.remove_session()

            return sync_wrapper

    return decorator(function) if function else partial(sqlalchemy_atomic_decorator, db_type=db_type, is_async=is_async)


def postgres_sqlalchemy_atomic_decorator(function: Callable[..., Any] | None = None) -> Callable[..., Any] | partial:
    """Decorator for PostgreSQL atomic transactions.

    Args:
        function (Callable | None): The function to wrap. If None, returns a partial function.

    Returns:
        Callable | partial: The wrapped function or a partial function for later use.
    """
    return sqlalchemy_atomic_decorator(db_type="postgres", function=function)


def async_postgres_sqlalchemy_atomic_decorator(
    function: Callable[..., Any] | None = None,
) -> Callable[..., Any] | partial:
    """Decorator for asynchronous PostgreSQL atomic transactions.

    Args:
        function (Callable | None): The function to wrap. If None, returns a partial function.

    Returns:
        Callable | partial: The wrapped function or a partial function for later use.
    """
    return sqlalchemy_atomic_decorator(db_type="postgres", is_async=True, function=function)


def sqlite_sqlalchemy_atomic_decorator(function: Callable[..., Any] | None = None) -> Callable[..., Any] | partial:
    """Decorator for SQLite atomic transactions.

    Args:
        function (Callable | None): The function to wrap. If None, returns a partial function.

    Returns:
        Callable | partial: The wrapped function or a partial function for later use.
    """
    return sqlalchemy_atomic_decorator(db_type="sqlite", function=function)


def async_sqlite_sqlalchemy_atomic_decorator(
    function: Callable[..., Any] | None = None,
) -> Callable[..., Any] | partial:
    """Decorator for asynchronous SQLite atomic transactions.

    Args:
        function (Callable | None): The function to wrap. If None, returns a partial function.

    Returns:
        Callable | partial: The wrapped function or a partial function for later use.
    """
    return sqlalchemy_atomic_decorator(db_type="sqlite", is_async=True, function=function)


def starrocks_sqlalchemy_atomic_decorator(
    function: Callable[..., Any] | None = None,
) -> Callable[..., Any] | partial:
    """Decorator for StarRocks atomic transactions.

    Args:
        function (Callable | None): The function to wrap. If None, returns a partial function.

    Returns:
        Callable | partial: The wrapped function or a partial function for later use.
    """
    return sqlalchemy_atomic_decorator(db_type="starrocks", function=function)


def async_starrocks_sqlalchemy_atomic_decorator(
    function: Callable[..., Any] | None = None,
) -> Callable[..., Any] | partial:
    """Decorator for asynchronous StarRocks atomic transactions.

    Args:
        function (Callable | None): The function to wrap. If None, returns a partial function.

    Returns:
        Callable | partial: The wrapped function or a partial function for later use.
    """
    return sqlalchemy_atomic_decorator(db_type="starrocks", is_async=True, function=function)
