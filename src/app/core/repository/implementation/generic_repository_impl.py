import math
from typing import Any, Dict, Generic, List, Type, TypeVar

from sqlmodel import SQLModel, delete, func, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.db.decorator import transactional
from src.app.core.model import Page, Pagination
from src.app.core.repository.interface import IBaseRepository
from src.app.core.repository.enum import JoinType
from src.app.core.repository.helpers.repository_helpers import RepositoryHelpers

T = TypeVar("T", bound=SQLModel)


class BaseRepository(IBaseRepository[T], Generic[T]):
    """
    Base implementation of the generic repository.
    Uses the IBaseRepository interface and Page/Pageable models for pagination.
    Includes useful methods inspired by TypeORM and JPA Repository.
    """

    def __init__(self, session: AsyncSession, entity_class: Type[T]):
        self.session = session
        self.entity_class = entity_class

    @transactional(readonly=False)
    async def save(self, entity: T) -> T:
        """
        Saves an entity to the database.

        Args:
            entity: The entity to save

        Returns:
            The saved entity
        """
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    @transactional(readonly=False)
    async def save_all(self, entities: List[T]) -> List[T]:
        """
        Saves multiple entities in a single transaction.

        Args:
            entities: List of entities to persist

        Returns:
            The list of saved and refreshed entities
        """
        if not entities:
            return []

        self.session.add_all(entities)
        await self.session.flush()

        for entity in entities:
            await self.session.refresh(entity)

        return entities

    @transactional(readonly=True)
    async def get_all(
        self,
        join_models: List[SQLModel] = None,
        where_conditions: Dict[str, Any] = None,
    ) -> List[T]:
        """
        Retrieves all entities ordered by ID.

        Args:
            join_models: Optional list of models to join against
            where_conditions: Optional complex where conditions

        Returns:
            A list of entities
        """
        stmt = select(self.entity_class).order_by(self.entity_class.id)
        stmt = RepositoryHelpers.apply_joins(stmt, join_models)
        stmt = RepositoryHelpers.apply_where_conditions(
            stmt, self.entity_class, where_conditions
        )

        results = await self.session.exec(stmt)
        return list(results.all())

    @transactional(readonly=True)
    async def get_by_id(self, entity_id: int) -> T | None:
        """
        Retrieves a single entity by its primary key.

        Args:
            entity_id: The entity ID

        Returns:
            The entity if found, otherwise None
        """
        stmt = select(self.entity_class).where(self.entity_class.id == entity_id)
        results = await self.session.exec(stmt)
        return results.first()

    @transactional(readonly=True)
    async def find_one_by(
        self,
        join_models: List[SQLModel] = None,
        where_conditions: Dict[str, Any] = None,
        **kwargs,
    ) -> T | None:
        """
        Finds a single entity by equality filters, with optional joins and where conditions.

        Args:
            join_models: Optional list of models to join against
            where_conditions: Optional complex where conditions
            **kwargs: Field=value equality filters

        Returns:
            The first matching entity or None
        """
        RepositoryHelpers.validate_fields(self.entity_class, kwargs)

        stmt = select(self.entity_class)
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.entity_class, key) == value)

        stmt = RepositoryHelpers.apply_joins(stmt, join_models)
        stmt = RepositoryHelpers.apply_where_conditions(
            stmt, self.entity_class, where_conditions
        )

        results = await self.session.exec(stmt)
        return results.first()

    @transactional(readonly=True)
    async def find_all_by(
        self,
        join_models: List[SQLModel] = None,
        where_conditions: Dict[str, Any] = None,
        **kwargs,
    ) -> List[T]:
        """
        Finds all entities that match the given equality filters.

        Args:
            join_models: Optional list of models to join against
            where_conditions: Optional complex where conditions
            **kwargs: Field=value equality filters

        Returns:
            A list of matching entities
        """
        RepositoryHelpers.validate_fields(self.entity_class, kwargs)

        stmt = select(self.entity_class).order_by(self.entity_class.id)
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.entity_class, key) == value)

        stmt = RepositoryHelpers.apply_joins(stmt, join_models)
        stmt = RepositoryHelpers.apply_where_conditions(
            stmt, self.entity_class, where_conditions
        )

        results = await self.session.exec(stmt)
        return list(results.all())

    @transactional(readonly=False)
    async def delete(self, entity_id: int) -> bool:
        """
        Deletes an entity by ID if it exists.

        Args:
            entity_id: The entity ID

        Returns:
            True if the entity was found and deleted, False otherwise
        """
        entity = await self.get_by_id(entity_id)
        if entity:
            await self.session.delete(entity)
            return True
        return False

    @transactional(readonly=False)
    async def delete_all_by(self, **kwargs) -> int:
        """
        Deletes all entities that match the provided equality filters.

        Args:
            **kwargs: Field=value equality filters

        Returns:
            The number of rows affected
        """
        RepositoryHelpers.validate_fields(self.entity_class, kwargs)

        stmt = delete(self.entity_class)
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.entity_class, key) == value)

        result = await self.session.exec(stmt)
        return result.rowcount

    @transactional(readonly=True)
    async def exists_by(self, **kwargs) -> bool:
        """
        Checks if any entity exists that matches the provided equality filters.

        Args:
            **kwargs: Field=value equality filters

        Returns:
            True if at least one entity exists, False otherwise
        """
        RepositoryHelpers.validate_fields(self.entity_class, kwargs)

        stmt = select(self.entity_class.id)
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.entity_class, key) == value)

        result = await self.session.exec(stmt)
        return result.first() is not None

    @transactional(readonly=True)
    async def count(self) -> int:
        """
        Counts all entities of this type.

        Returns:
            Total number of entities
        """
        stmt = select(func.count(self.entity_class.id))
        result = await self.session.exec(stmt)
        return result.first() or 0

    @transactional(readonly=True)
    async def count_by(self, **kwargs) -> int:
        """
        Counts entities matching the provided equality filters.

        Args:
            **kwargs: Field=value equality filters

        Returns:
            Number of matching entities
        """
        RepositoryHelpers.validate_fields(self.entity_class, kwargs)

        stmt = select(func.count(self.entity_class.id))
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.entity_class, key) == value)

        result = await self.session.exec(stmt)
        return result.first() or 0

    @transactional(readonly=True)
    async def find_by_ids(self, entity_ids: List[int]) -> List[T]:
        """
        Finds all entities whose IDs are in the given list.

        Args:
            entity_ids: List of IDs

        Returns:
            A list of entities (empty if none found or input empty)
        """
        if not entity_ids:
            return []

        stmt = select(self.entity_class).where(self.entity_class.id.in_(entity_ids))
        results = await self.session.exec(stmt)
        return list(results.all())

    @transactional(readonly=False)
    async def delete_by_ids(self, entity_ids: List[int]) -> bool:
        """
        Deletes all entities whose IDs are in the given list, only if all IDs exist.

        Args:
            entity_ids: List of IDs to delete

        Returns:
            True if all entities were found and deleted, False otherwise
        """
        if not entity_ids:
            return True

        stmt = select(self.entity_class).where(self.entity_class.id.in_(entity_ids))
        results = await self.session.exec(stmt)
        entities = list(results.all())

        found_ids = {entity.id for entity in entities}
        if len(found_ids) != len(entity_ids):
            return False

        for entity in entities:
            await self.session.delete(entity)

        return True

    @transactional(readonly=False)
    async def update_by_id(
        self, entity_id: int, update_data: Dict[str, Any]
    ) -> T | None:
        """
        Updates fields of a single entity by ID.

        Args:
            entity_id: The entity ID
            update_data: Dict of field updates

        Returns:
            The updated entity, or None if not found
        """
        RepositoryHelpers.validate_fields(self.entity_class, update_data)

        entity = await self.get_by_id(entity_id)
        if not entity:
            return None

        for key, value in update_data.items():
            setattr(entity, key, value)

        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    @transactional(readonly=False)
    async def update_all_by(
        self, filters: Dict[str, Any], update_data: Dict[str, Any]
    ) -> int:
        """
        Updates one or more entities that match the provided filters.

        Args:
            filters: Field=value equality filters
            update_data: Dict of field updates

        Returns:
            Number of rows affected
        """
        RepositoryHelpers.validate_fields(self.entity_class, {**filters, **update_data})

        stmt = update(self.entity_class).values(**update_data)
        for key, value in filters.items():
            stmt = stmt.where(getattr(self.entity_class, key) == value)

        result = await self.session.exec(stmt)
        return result.rowcount

    @transactional(readonly=True)
    async def get_pageable(
        self,
        page: int,
        size: int,
        join_models: List[SQLModel] = None,
        where_conditions: Dict[str, Any] = None,
    ) -> Page:
        """
        Retrieves a page of entities with optional joins and complex where conditions.

        Args:
            page: Page number starting at 1
            size: Page size
            join_models: Optional list of models to join against
            where_conditions: Optional complex where conditions

        Returns:
            A Page containing serialized data and pagination metadata
        """
        if page < 1:
            page = 1
        if size < 1:
            size = 10

        offset = (page - 1) * size

        stmt = (
            select(self.entity_class)
            .order_by(self.entity_class.id)
            .offset(offset)
            .limit(size)
        )
        stmt = RepositoryHelpers.apply_joins(stmt, join_models)
        stmt = RepositoryHelpers.apply_where_conditions(
            stmt, self.entity_class, where_conditions
        )

        results = await self.session.exec(stmt)
        entities = [entity.model_dump() for entity in results.all()]

        count_stmt = select(func.count(self.entity_class.id))
        count_stmt = RepositoryHelpers.apply_joins(count_stmt, join_models)
        count_stmt = RepositoryHelpers.apply_where_conditions(
            count_stmt, self.entity_class, where_conditions
        )

        count_result = await self.session.exec(count_stmt)
        total_items = count_result.first() or 0

        total_pages = math.ceil(total_items / size) if total_items > 0 else 1
        next_page = page + 1 if page < total_pages else None
        previous_page = page - 1 if page > 1 else None

        page_info = Pagination(
            current_page=page,
            per_page=size,
            total=total_items,
            total_pages=total_pages,
            next_page=next_page,
            previous_page=previous_page,
        )

        return Page(data=entities, meta=page_info)

    @transactional(readonly=True)
    async def get_pageable_by(
        self,
        page: int,
        size: int,
        join_models: List[SQLModel] = None,
        where_conditions: Dict[str, Any] = None,
        **kwargs,
    ) -> Page:
        """
        Retrieves a page of entities filtered by equality filters, with optional joins and where conditions.

        Args:
            page: Page number starting at 1
            size: Page size
            join_models: Optional list of models to join against
            where_conditions: Optional complex where conditions
            **kwargs: Field=value equality filters

        Returns:
            A Page containing serialized data and pagination metadata
        """
        RepositoryHelpers.validate_fields(self.entity_class, kwargs)

        if page < 1:
            page = 1
        if size < 1:
            size = 10

        offset = (page - 1) * size

        stmt = select(self.entity_class).order_by(self.entity_class.id)
        count_stmt = select(func.count(self.entity_class.id))

        for key, value in kwargs.items():
            filter_condition = getattr(self.entity_class, key) == value
            stmt = stmt.where(filter_condition)
            count_stmt = count_stmt.where(filter_condition)

        stmt = RepositoryHelpers.apply_joins(stmt, join_models)
        stmt = RepositoryHelpers.apply_where_conditions(
            stmt, self.entity_class, where_conditions
        )

        count_stmt = RepositoryHelpers.apply_joins(count_stmt, join_models)
        count_stmt = RepositoryHelpers.apply_where_conditions(
            count_stmt, self.entity_class, where_conditions
        )

        stmt = stmt.offset(offset).limit(size)

        results = await self.session.exec(stmt)
        entities = [entity.model_dump() for entity in results.all()]

        count_result = await self.session.exec(count_stmt)
        total_items = count_result.first() or 0

        total_pages = math.ceil(total_items / size) if total_items > 0 else 1
        next_page = page + 1 if page < total_pages else None
        previous_page = page - 1 if page > 1 else None

        page_info = Pagination(
            current_page=page,
            per_page=size,
            total=total_items,
            total_pages=total_pages,
            next_page=next_page,
            previous_page=previous_page,
        )

        return Page(data=entities, meta=page_info)

    @transactional(readonly=True)
    async def find_pageables(
        self,
        page: int,
        size: int,
        join_models: List[SQLModel] = None,
        join_type: JoinType = JoinType.INNER,
        where_conditions: Dict[str, Any] = None,
        filters: Dict[str, Any] = None,
    ) -> Page:
        """
        Gets a page of entities with support for JOINs and multiple WHERE filters.

        Args:
            page: Page number (starting from 1)
            size: Page size
            join_models: Optional list of models to JOIN with
            join_type: JOIN type (INNER by default, LEFT_OUTER)
            where_conditions: Complex WHERE conditions (dict with operators)
            filters: Simple equality filters (dict with field: value)

        Returns:
            Page object with data and pagination metadata
        """
        # Validar parámetros de entrada
        if page < 1:
            page = 1
        if size < 1:
            size = 10

        if filters:
            RepositoryHelpers.validate_fields(self.entity_class, filters)

        offset = (page - 1) * size

        stmt = (
            select(self.entity_class)
            .order_by(self.entity_class.id)
            .offset(offset)
            .limit(size)
        )
        count_stmt = select(func.count(self.entity_class.id))

        if filters:
            for key, value in filters.items():
                filter_condition = getattr(self.entity_class, key) == value
                stmt = stmt.where(filter_condition)
                count_stmt = count_stmt.where(filter_condition)

        stmt = RepositoryHelpers.apply_joins(stmt, join_models, join_type)
        count_stmt = RepositoryHelpers.apply_joins(count_stmt, join_models, join_type)

        stmt = RepositoryHelpers.apply_where_conditions(
            stmt, self.entity_class, where_conditions
        )
        count_stmt = RepositoryHelpers.apply_where_conditions(
            count_stmt, self.entity_class, where_conditions
        )

        results = await self.session.exec(stmt)
        entities = [entity.model_dump() for entity in results.all()]

        count_result = await self.session.exec(count_stmt)
        total_items = count_result.first() or 0

        total_pages = math.ceil(total_items / size) if total_items > 0 else 1
        next_page = page + 1 if page < total_pages else None
        previous_page = page - 1 if page > 1 else None

        page_info = Pagination(
            current_page=page,
            per_page=size,
            total=total_items,
            total_pages=total_pages,
            next_page=next_page,
            previous_page=previous_page,
        )

        return Page(data=entities, meta=page_info)

    @transactional(readonly=False)
    async def save_or_update(self, entity: T) -> T:
        """
        Saves a new entity or updates an existing one if its ID already exists.

        Args:
            entity: The entity to save or update

        Returns:
            The persisted entity
        """
        if hasattr(entity, "id") and entity.id is not None:
            existing = await self.get_by_id(entity.id)
            if existing:
                for key, value in entity.model_dump(exclude_unset=True).items():
                    if key != "id":
                        setattr(existing, key, value)
                await self.session.flush()
                await self.session.refresh(existing)
                return existing
        return await self.save(entity)

    @transactional(readonly=True)
    async def find_all_ordered_by(
        self,
        order_field: str,
        ascending: bool = True,
        join_models: List[SQLModel] = None,
        where_conditions: Dict[str, Any] = None,
        **kwargs,
    ) -> List[T]:
        """
        Finds all entities ordered by a given field.

        Args:
            order_field: Field name to order by
            ascending: True for ascending, False for descending
            join_models: Optional list of models to join against (unused here, reserved)
            where_conditions: Optional complex where conditions (unused here, reserved)
            **kwargs: Additional equality filters

        Returns:
            A list of entities ordered accordingly
        """
        return await RepositoryHelpers.find_all_ordered_by(
            self.session, self.entity_class, order_field, ascending, **kwargs
        )

    @transactional(readonly=True)
    async def find_first_ordered_by(
        self, order_field: str, ascending: bool = True, **kwargs
    ) -> T | None:
        """
        Finds the first entity ordered by a given field.

        Args:
            order_field: Field name to order by
            ascending: True for ascending, False for descending
            **kwargs: Additional equality filters

        Returns:
            The first matching entity or None
        """
        return await RepositoryHelpers.find_first_ordered_by(
            self.session, self.entity_class, order_field, ascending, **kwargs
        )

    @transactional(readonly=True)
    async def find_last_ordered_by(
        self, order_field: str, ascending: bool = True, **kwargs
    ) -> T | None:
        """
        Finds the last entity ordered by a given field.

        Args:
            order_field: Field name to order by
            ascending: True for ascending, False for descending
            **kwargs: Additional equality filters

        Returns:
            The last matching entity or None
        """
        return await RepositoryHelpers.find_last_ordered_by(
            self.session, self.entity_class, order_field, ascending, **kwargs
        )

    @transactional(readonly=True)
    async def exists_by_id(self, entity_id: int) -> bool:
        """
        Checks whether an entity with the given ID exists.

        Args:
            entity_id: The entity ID

        Returns:
            True if exists, False otherwise
        """
        entity = await self.get_by_id(entity_id)
        return entity is not None

    @transactional(readonly=True)
    async def find_all_in_range(
        self, field_name: str, min_value: Any, max_value: Any
    ) -> List[T]:
        """
        Finds all entities where a numeric or comparable field is within a range.

        Args:
            field_name: Name of the field
            min_value: Minimum value (inclusive)
            max_value: Maximum value (inclusive)

        Returns:
            A list of matching entities
        """
        return await RepositoryHelpers.find_all_in_range(
            self.session, self.entity_class, field_name, min_value, max_value
        )

    @transactional(readonly=True)
    async def find_all_like(self, field_name: str, pattern: str) -> List[T]:
        """
        Finds all entities whose field matches a SQL LIKE pattern.

        Args:
            field_name: Name of the field
            pattern: SQL LIKE pattern (e.g., "%abc%")

        Returns:
            A list of matching entities
        """
        return await RepositoryHelpers.find_all_like(
            self.session, self.entity_class, field_name, pattern
        )

    @transactional(readonly=True)
    async def find_all_in_list(self, field_name: str, values: List[Any]) -> List[T]:
        """
        Finds all entities where the field value is in the provided list.

        Args:
            field_name: Name of the field
            values: List of allowed values

        Returns:
            A list of matching entities
        """
        return await RepositoryHelpers.find_all_in_list(
            self.session, self.entity_class, field_name, values
        )

    @transactional(readonly=True)
    async def find_all_not_in_list(self, field_name: str, values: List[Any]) -> List[T]:
        """
        Finds all entities where the field value is NOT in the provided list.

        Args:
            field_name: Name of the field
            values: List of excluded values

        Returns:
            A list of matching entities
        """
        return await RepositoryHelpers.find_all_not_in_list(
            self.session, self.entity_class, field_name, values
        )

    @transactional(readonly=True)
    async def get_distinct_values(self, field_name: str) -> List[Any]:
        """
        Retrieves distinct values for a given field.

        Args:
            field_name: Name of the field

        Returns:
            A list of unique values
        """
        return await RepositoryHelpers.get_distinct_values(
            self.session, self.entity_class, field_name
        )

    @transactional(readonly=True)
    async def find_all_greater_than(self, field_name: str, value: Any) -> List[T]:
        """
        Finds all entities where the field value is greater than the given value.

        Args:
            field_name: Name of the field
            value: Threshold value

        Returns:
            A list of matching entities
        """
        return await RepositoryHelpers.find_all_greater_than(
            self.session, self.entity_class, field_name, value
        )

    @transactional(readonly=True)
    async def find_all_less_than(self, field_name: str, value: Any) -> List[T]:
        """
        Finds all entities where the field value is less than the given value.

        Args:
            field_name: Name of the field
            value: Threshold value

        Returns:
            A list of matching entities
        """
        return await RepositoryHelpers.find_all_less_than(
            self.session, self.entity_class, field_name, value
        )

    @transactional(readonly=True)
    async def find_all_between_dates(
        self, field_name: str, start_date: Any, end_date: Any
    ) -> List[T]:
        """
        Finds all entities where a date/datetime field is between two values.

        Args:
            field_name: Name of the date/datetime field
            start_date: Start of the range (inclusive)
            end_date: End of the range (inclusive)

        Returns:
            A list of matching entities
        """
        return await RepositoryHelpers.find_all_between_dates(
            self.session, self.entity_class, field_name, start_date, end_date
        )

    @transactional(readonly=False)
    async def soft_delete_by_id(
        self, entity_id: int, deleted_field: str = "deleted"
    ) -> bool:
        """
        Performs a soft delete by toggling the given deleted flag field.

        Args:
            entity_id: The entity ID
            deleted_field: Name of the boolean field used for soft delete

        Returns:
            True if updated successfully, False otherwise
        """
        return await RepositoryHelpers.soft_delete_by_id(
            self.session, self.entity_class, entity_id, deleted_field
        )

    @transactional(readonly=False)
    async def restore_by_id(
        self, entity_id: int, deleted_field: str = "deleted"
    ) -> bool:
        """
        Restores a soft-deleted entity by toggling the deleted flag off.

        Args:
            entity_id: The entity ID
            deleted_field: Name of the boolean field used for soft delete

        Returns:
            True if updated successfully, False otherwise
        """
        return await RepositoryHelpers.restore_by_id(
            self.session, self.entity_class, entity_id, deleted_field
        )

    @transactional(readonly=True)
    async def find_all_active(self, active_field: str = "active") -> List[T]:
        """
        Finds all entities where the active flag is True.

        Args:
            active_field: Name of the boolean field indicating active status

        Returns:
            A list of active entities
        """
        return await self.find_all_by(**{active_field: True})

    @transactional(readonly=True)
    async def find_all_inactive(self, active_field: str = "active") -> List[T]:
        """
        Finds all entities where the active flag is False.

        Args:
            active_field: Name of the boolean field indicating active status

        Returns:
            A list of inactive entities
        """
        return await self.find_all_by(**{active_field: False})

    @transactional(readonly=False)
    async def bulk_update_field(
        self, entity_ids: List[int], field_name: str, new_value: Any
    ) -> int:
        """
        Bulk-updates a single field for multiple entities by IDs.

        Args:
            entity_ids: List of IDs to update
            field_name: Field to update
            new_value: New value to set

        Returns:
            Number of rows affected
        """
        return await RepositoryHelpers.bulk_update_field(
            self.session, self.entity_class, entity_ids, field_name, new_value
        )

    @transactional(readonly=True)
    async def find_random(self, limit: int = 1) -> List[T]:
        """
        Retrieves a random set of entities.

        Args:
            limit: Maximum number of entities to return

        Returns:
            A list with up to 'limit' random entities
        """
        return await RepositoryHelpers.find_random(
            self.session, self.entity_class, limit
        )
