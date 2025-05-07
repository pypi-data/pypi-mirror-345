from enum import Enum
from typing import Any, override
from uuid import UUID

from sqlalchemy import Delete, Executable, Result, ScalarResult, Update, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, Session
from sqlalchemy.sql import Select

from archipy.adapters.base.sqlalchemy.ports import AnyExecuteParams, AsyncSQLAlchemyPort, SQLAlchemyPort
from archipy.adapters.base.sqlalchemy.session_managers import (
    AsyncBaseSQLAlchemySessionManager,
    BaseSQLAlchemySessionManager,
)
from archipy.configs.base_config import BaseConfig
from archipy.configs.config_template import SQLAlchemyConfig
from archipy.models.dtos.pagination_dto import PaginationDTO
from archipy.models.dtos.sort_dto import SortDTO
from archipy.models.entities import BaseEntity
from archipy.models.errors.custom_errors import InternalError, InvalidArgumentError, InvalidEntityTypeError
from archipy.models.types.base_types import FilterOperationType
from archipy.models.types.sort_order_type import SortOrderType


class SQLAlchemyFilterMixin:
    """Mixin providing filtering capabilities for SQLAlchemy queries.

    Supports equality, inequality, string operations, list operations, and NULL checks.
    """

    @staticmethod
    def _apply_filter(
        query: Select | Update | Delete,
        field: InstrumentedAttribute,
        value: Any,
        operation: FilterOperationType,
    ) -> Select | Update | Delete:
        """Apply a filter to a SQLAlchemy query based on the specified operation.

        Args:
            query: The SQLAlchemy query to apply the filter to.
            field: The model attribute/column to filter on.
            value: The value to compare against.
            operation: The type of filter operation to apply.

        Returns:
            The updated query with the filter applied.
        """
        if value is not None or operation in [FilterOperationType.IS_NULL, FilterOperationType.IS_NOT_NULL]:
            match operation:
                case FilterOperationType.EQUAL:
                    return query.where(field == value)
                case FilterOperationType.NOT_EQUAL:
                    return query.where(field != value)
                case FilterOperationType.LESS_THAN:
                    return query.where(field < value)
                case FilterOperationType.LESS_THAN_OR_EQUAL:
                    return query.where(field <= value)
                case FilterOperationType.GREATER_THAN:
                    return query.where(field > value)
                case FilterOperationType.GREATER_THAN_OR_EQUAL:
                    return query.where(field >= value)
                case FilterOperationType.IN_LIST:
                    return query.where(field.in_(value))
                case FilterOperationType.NOT_IN_LIST:
                    return query.where(~field.in_(value))
                case FilterOperationType.LIKE:
                    return query.where(field.like(f"%{value}%"))
                case FilterOperationType.ILIKE:
                    return query.where(field.ilike(f"%{value}%"))
                case FilterOperationType.STARTS_WITH:
                    return query.where(field.startswith(value))
                case FilterOperationType.ENDS_WITH:
                    return query.where(field.endswith(value))
                case FilterOperationType.CONTAINS:
                    return query.where(field.contains(value))
                case FilterOperationType.IS_NULL:
                    return query.where(field.is_(None))
                case FilterOperationType.IS_NOT_NULL:
                    return query.where(field.isnot(None))
        return query


class SQLAlchemyPaginationMixin:
    """Mixin providing pagination capabilities for SQLAlchemy queries.

    Supports limiting results and applying offsets for paginated queries.
    """

    @staticmethod
    def _apply_pagination(query: Select, pagination: PaginationDTO | None) -> Select:
        """Apply pagination to a SQLAlchemy query.

        Args:
            query: The SQLAlchemy query to paginate.
            pagination: Pagination settings (page size and offset).

        Returns:
            The paginated query.
        """
        if pagination is None:
            return query
        return query.limit(pagination.page_size).offset(pagination.offset)


class SQLAlchemySortMixin:
    """Mixin providing sorting capabilities for SQLAlchemy queries.

    Supports dynamic column selection and ascending/descending order.
    """

    @staticmethod
    def _apply_sorting(entity: type[BaseEntity], query: Select, sort_info: SortDTO | None) -> Select:
        """Apply sorting to a SQLAlchemy query.

        Args:
            entity: The entity class to query.
            query: The SQLAlchemy query to sort.
            sort_info: Sorting information (column and direction).

        Returns:
            The sorted query.

        Raises:
            InvalidArgumentError: If the sort order is invalid.
        """
        if sort_info is None:
            return query
        if isinstance(sort_info.column, str):
            sort_column = getattr(entity, sort_info.column)
        elif isinstance(sort_info.column, Enum):
            sort_column = getattr(entity, sort_info.column.name.lower())
        else:
            sort_column = sort_info.column

        order_value = sort_info.order.value if isinstance(sort_info.order, Enum) else sort_info.order
        match order_value:
            case SortOrderType.ASCENDING.value:
                return query.order_by(sort_column.asc())
            case SortOrderType.DESCENDING.value:
                return query.order_by(sort_column.desc())
            case _:
                raise InvalidArgumentError(argument_name="sort_info.order")


class BaseSQLAlchemyAdapter(SQLAlchemyPort, SQLAlchemyPaginationMixin, SQLAlchemySortMixin, SQLAlchemyFilterMixin):
    """Base synchronous SQLAlchemy adapter for ORM operations.

    Provides a standardized interface for CRUD operations, pagination, sorting, and filtering.
    Specific database adapters should inherit from this class and provide their own session manager.

    Args:
        orm_config: Configuration for SQLAlchemy. If None, uses global config.
    """

    def __init__(self, orm_config: SQLAlchemyConfig | None = None) -> None:
        """Initialize the base adapter with a session manager.

        Args:
            orm_config: Configuration for SQLAlchemy. If None, uses global config.
        """
        configs = BaseConfig.global_config().SQLALCHEMY if orm_config is None else orm_config
        self.session_manager: BaseSQLAlchemySessionManager = self._create_session_manager(configs)

    def _create_session_manager(self, configs: SQLAlchemyConfig) -> BaseSQLAlchemySessionManager:
        """Create a session manager for the specific database.

        Args:
            configs: SQLAlchemy configuration.

        Returns:
            A session manager instance.
        """
        return BaseSQLAlchemySessionManager(configs)

    @override
    def execute_search_query(
        self,
        entity: type[BaseEntity],
        query: Select,
        pagination: PaginationDTO | None = None,
        sort_info: SortDTO | None = None,
    ) -> tuple[list[BaseEntity], int]:
        """Execute a search query with pagination and sorting.

        Args:
            entity: The entity class to query.
            query: The SQLAlchemy SELECT query.
            pagination: Optional pagination settings.
            sort_info: Optional sorting information.

        Returns:
            Tuple of the list of entities and the total count.

        Raises:
            InternalError: If the database query fails.
        """
        try:
            sort_info = sort_info or SortDTO.default()
            session = self.get_session()
            sorted_query = self._apply_sorting(entity, query, sort_info)
            paginated_query = self._apply_pagination(sorted_query, pagination)
            result_set = session.execute(paginated_query)
            results = list(result_set.scalars().all())

            count_query = select(func.count()).select_from(query.subquery())
            total_count = session.execute(count_query).scalar_one()
        except Exception as e:
            raise InternalError(details=f"Database query failed: {e!s}") from e
        return results, total_count

    @override
    def get_session(self) -> Session:
        return self.session_manager.get_session()

    @override
    def create(self, entity: BaseEntity) -> BaseEntity | None:
        """Creates a new entity in the database.

        Args:
            entity (BaseEntity): The entity to be created.

        Returns:
            BaseEntity | None: The created entity with updated attributes
                (e.g., generated ID), or None if creation failed.

        Raises:
            InvalidEntityTypeError: If the provided entity is not a BaseEntity.
        """
        if not isinstance(entity, BaseEntity):
            raise InvalidEntityTypeError(entity, BaseEntity)
        try:
            session = self.get_session()
            session.add(entity)
            session.flush()
        except Exception as e:
            raise InternalError(details=f"Entity creation failed: {e!s}") from e
        return entity

    @override
    def bulk_create(self, entities: list[BaseEntity]) -> list[BaseEntity] | None:
        """Creates multiple entities in a single database operation.

        Args:
            entities: List of entity objects to create.

        Returns:
            The list of created entities with updated attributes (e.g., generated IDs),
            or None if creation failed.

        Raises:
            InvalidEntityTypeError: If any of the provided entities is not a BaseEntity.
            InternalError: If the database operation fails.
        """
        # Check that all entities are valid
        for entity in entities:
            if not isinstance(entity, BaseEntity):
                raise InvalidEntityTypeError(entity, BaseEntity)

        try:
            session = self.get_session()
            session.add_all(entities)
            session.flush()
        except Exception as e:
            raise InternalError(details=f"Bulk create operation failed: {e!s}") from e
        return entities

    @override
    def get_by_uuid(self, entity_type: type, entity_uuid: UUID) -> BaseEntity | None:
        """Retrieves an entity by its UUID.

        Args:
            entity_type (type): The entity class to query.
            entity_uuid (UUID): The UUID of the entity to retrieve.

        Returns:
            Any: The retrieved entity or None if not found.

        Raises:
            InvalidEntityTypeError: If entity_type is not a subclass of BaseEntity
                or if entity_uuid is not a UUID.
        """
        if not issubclass(entity_type, BaseEntity):
            raise InvalidEntityTypeError(entity_type, BaseEntity)
        if not isinstance(entity_uuid, UUID):
            raise InvalidEntityTypeError(entity_uuid, UUID)
        try:
            session = self.get_session()
            return session.get(entity_type, entity_uuid)
        except Exception as e:
            raise InternalError(details=f"Entity retrieval by UUID failed: {e!s}") from e

    @override
    def delete(self, entity: BaseEntity) -> None:
        if not isinstance(entity, BaseEntity):
            raise InvalidEntityTypeError(entity, BaseEntity)
        try:
            session = self.get_session()
            session.delete(entity)
        except Exception as e:
            raise InternalError(details=f"Entity deletion failed: {e!s}") from e

    @override
    def bulk_delete(self, entities: list[BaseEntity]) -> None:
        """Deletes multiple entities in a sequence of operations.

        Args:
            entities: List of entity objects to delete.

        Raises:
            InvalidEntityTypeError: If any of the provided entities is not a BaseEntity.
            InternalError: If the database operation fails.
        """
        try:
            for entity in entities:
                if not isinstance(entity, BaseEntity):
                    raise InvalidEntityTypeError(entity, BaseEntity)
                self.delete(entity)
        except Exception as e:
            raise InternalError(details=f"Bulk delete operation failed: {e!s}") from e

    @override
    def execute(self, statement: Executable, params: AnyExecuteParams | None = None) -> Result[Any]:
        """Executes a raw SQL statement.

        Args:
            statement: The SQLAlchemy statement to execute.
            params: Optional parameters for the statement.

        Returns:
            The execution result.

        Raises:
            InternalError: If the statement execution fails.
        """
        try:
            session = self.get_session()
            return session.execute(statement, params)
        except Exception as e:
            raise InternalError(details=f"Statement execution failed: {e!s}") from e

    @override
    def scalars(self, statement: Executable, params: AnyExecuteParams | None = None) -> ScalarResult[Any]:
        """Executes a statement and returns the scalar result.

        This is a convenience method that executes a statement and
        returns the scalar result directly.

        Args:
            statement: The SQLAlchemy statement to execute.
            params: Optional parameters for the statement.

        Returns:
            The scalar result of executing the statement.

        Raises:
            InternalError: If the statement execution fails.
        """
        try:
            session = self.get_session()
            return session.scalars(statement, params)
        except Exception as e:
            raise InternalError(details=f"Scalar query failed: {e!s}") from e


class AsyncBaseSQLAlchemyAdapter(
    AsyncSQLAlchemyPort,
    SQLAlchemyPaginationMixin,
    SQLAlchemySortMixin,
    SQLAlchemyFilterMixin,
):
    """Base asynchronous SQLAlchemy adapter for ORM operations.

    Provides an async interface for CRUD operations, pagination, sorting, and filtering.
    Specific database adapters should inherit from this class and provide their own session manager.

    Args:
        orm_config: Configuration for SQLAlchemy. If None, uses global config.
    """

    def __init__(self, orm_config: SQLAlchemyConfig | None = None) -> None:
        """Initialize the base async adapter with a session manager.

        Args:
            orm_config: Configuration for SQLAlchemy. If None, uses global config.
        """
        configs = BaseConfig.global_config().SQLALCHEMY if orm_config is None else orm_config
        self.session_manager: AsyncBaseSQLAlchemySessionManager = self._create_async_session_manager(configs)

    def _create_async_session_manager(self, configs: SQLAlchemyConfig) -> AsyncBaseSQLAlchemySessionManager:
        """Create an async session manager for the specific database.

        Args:
            configs: SQLAlchemy configuration.

        Returns:
            An async session manager instance.
        """
        return AsyncBaseSQLAlchemySessionManager(configs)

    @override
    async def execute_search_query(
        self,
        entity: type[BaseEntity],
        query: Select,
        pagination: PaginationDTO | None,
        sort_info: SortDTO | None = None,
    ) -> tuple[list[BaseEntity], int]:
        """Execute a search query with pagination and sorting.

        This method executes a SELECT query with pagination and sorting applied,
        and returns both the results and the total count of matching records.

        Args:
            entity: The entity class to query
            query: The SQLAlchemy SELECT query
            pagination: Pagination settings (page number and page size)
            sort_info: Sorting information (column and direction)

        Returns:
            A tuple containing:
                - List of entities matching the query
                - Total count of matching records (ignoring pagination)

        Raises:
            InvalidEntityTypeError: If the entity type is invalid
            InternalError: If the database query fails for any other reason
        """
        try:
            sort_info = sort_info or SortDTO.default()

            session = self.get_session()
            sorted_query = self._apply_sorting(entity, query, sort_info)
            paginated_query = self._apply_pagination(sorted_query, pagination)

            result_set = await session.execute(paginated_query)
            results = list(result_set.scalars().all())

            count_query = select(func.count()).select_from(query.subquery())
            count_result = await session.execute(count_query)
            total_count = count_result.scalar_one()
        except Exception as e:
            raise InternalError(details=f"Database query failed: {e!s}") from e
        return results, total_count

    @override
    def get_session(self) -> AsyncSession:
        return self.session_manager.get_session()

    @override
    async def create(self, entity: BaseEntity) -> BaseEntity | None:
        if not isinstance(entity, BaseEntity):
            raise InvalidEntityTypeError(entity, BaseEntity)
        try:
            session: AsyncSession = self.get_session()
            session.add(entity)
            await session.flush()
        except Exception as e:
            raise InternalError(details=f"Async entity creation failed: {e!s}") from e
        return entity

    @override
    async def bulk_create(self, entities: list[BaseEntity]) -> list[BaseEntity] | None:
        """Creates multiple entities in a single asynchronous database operation.

        Args:
            entities: List of entity objects to create.

        Returns:
            The list of created entities with updated attributes (e.g., generated IDs),
            or None if creation failed.

        Raises:
            InvalidEntityTypeError: If any of the provided entities is not a BaseEntity.
            InternalError: If the database operation fails.
        """
        # Check that all entities are valid
        for entity in entities:
            if not isinstance(entity, BaseEntity):
                raise InvalidEntityTypeError(entity, BaseEntity)

        try:
            session = self.get_session()
            session.add_all(entities)
            await session.flush()
        except Exception as e:
            raise InternalError(details=f"Async bulk create operation failed: {e!s}") from e
        return entities

    @override
    async def get_by_uuid(self, entity_type: type, entity_uuid: UUID) -> Any | None:
        if not issubclass(entity_type, BaseEntity):
            raise InvalidEntityTypeError(entity_type, BaseEntity)
        if not isinstance(entity_uuid, UUID):
            raise InvalidEntityTypeError(entity_uuid, UUID)
        try:
            session = self.get_session()
            return await session.get(entity_type, entity_uuid)
        except Exception as e:
            raise InternalError(details=f"Async entity retrieval by UUID failed: {e!s}") from e

    @override
    async def delete(self, entity: BaseEntity) -> None:
        if not isinstance(entity, BaseEntity):
            raise InvalidEntityTypeError(entity, BaseEntity)
        try:
            session = self.get_session()
            await session.delete(entity)
        except Exception as e:
            raise InternalError(details=f"Async entity deletion failed: {e!s}") from e

    @override
    async def bulk_delete(self, entities: list[BaseEntity]) -> None:
        try:
            for entity in entities:
                await self.delete(entity)
        except Exception as e:
            raise InternalError(details=f"Async bulk delete operation failed: {e!s}") from e

    @override
    async def execute(self, statement: Executable, params: AnyExecuteParams | None = None) -> Result[Any]:
        """Executes a raw SQL statement asynchronously.

        Args:
            statement: The SQLAlchemy statement to execute.
            params: Optional parameters for the statement.

        Returns:
            The asynchronous execution result.

        Raises:
            InternalError: If the statement execution fails.
        """
        try:
            session = self.get_session()
            return await session.execute(statement, params)
        except Exception as e:
            raise InternalError(details=f"Async statement execution failed: {e!s}") from e

    @override
    async def scalars(self, statement: Executable, params: AnyExecuteParams | None = None) -> ScalarResult[Any]:
        """Executes a statement and returns the scalar result asynchronously.

        This is a convenience method that executes a statement and
        returns the scalar result directly using async operations.

        Args:
            statement: The SQLAlchemy statement to execute.
            params: Optional parameters for the statement.

        Returns:
            The scalar result of executing the statement asynchronously.

        Raises:
            InternalError: If the statement execution fails.
        """
        try:
            session = self.get_session()
            return await session.scalars(statement, params)
        except Exception as e:
            raise InternalError(details=f"Async scalar query failed: {e!s}") from e
