from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, TypeVar

from sqlmodel import SQLModel

from src.app.core.model import Page
from src.app.core.repository.enum import JoinType

T = TypeVar("T", bound=SQLModel)


class IBaseRepository(ABC, Generic[T]):
    """
    Generic interface for repositories.
    Defines the contract for repository operations with support for JOINs and WHERE conditions.
    """

    @abstractmethod
    async def save(self, entity: T) -> T:
        """
        Saves an entity to the database.

        Args:
            entity: The entity to save

        Returns:
            The saved entity
        """
        pass

    @abstractmethod
    async def save_all(self, entities: List[T]) -> List[T]:
        """
        Saves multiple entities to the database.

        Args:
            entities: List of entities to save

        Returns:
            List of saved entities
        """
        pass

    @abstractmethod
    async def get_all(
        self,
        join_models: List[SQLModel] = None,
        where_conditions: Dict[str, Any] = None,
    ) -> List[T]:
        """
        Gets all entities with optional JOINs and WHERE conditions.

        Args:
            join_models: Optional list of models to JOIN with
            where_conditions: Additional WHERE conditions

        Returns:
            List of all entities
        """
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: int) -> T | None:
        """
        Gets an entity by its ID.

        Args:
            entity_id: Entity ID

        Returns:
            The entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_one_by(
        self,
        join_models: List[SQLModel] = None,
        where_conditions: Dict[str, Any] = None,
        **kwargs,
    ) -> T | None:
        """
        Finds the first entity matching the given criteria.

        Args:
            join_models: Optional list of models to JOIN with
            where_conditions: Additional WHERE conditions
            **kwargs: Fields and values for search

        Returns:
            The first entity found or None
        """
        pass

    @abstractmethod
    async def find_all_by(
        self,
        join_models: List[SQLModel] = None,
        where_conditions: Dict[str, Any] = None,
        **kwargs,
    ) -> List[T]:
        """
        Finds all entities matching the given criteria.

        Args:
            join_models: Optional list of models to JOIN with
            where_conditions: Additional WHERE conditions
            **kwargs: Fields and values for search

        Returns:
            List of entities found
        """
        pass

    @abstractmethod
    async def delete(self, entity_id: int) -> bool:
        """
        Deletes an entity by its ID.

        Args:
            entity_id: ID of the entity to delete

        Returns:
            True if deleted successfully, False if not found
        """
        pass

    @abstractmethod
    async def delete_all_by(self, **kwargs) -> int:
        """
        Deletes all entities matching the given criteria.

        Args:
            **kwargs: Fields and values to filter entities to delete

        Returns:
            Number of entities deleted
        """
        pass

    @abstractmethod
    async def exists_by(self, **kwargs) -> bool:
        """
        Checks if an entity exists matching the given criteria.

        Args:
            **kwargs: Fields and values for search

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def count(self) -> int:
        """
        Counts the total number of entities in the table.

        Returns:
            Total number of entities
        """
        pass

    @abstractmethod
    async def count_by(self, **kwargs) -> int:
        """
        Counts entities matching the given criteria.

        Args:
            **kwargs: Fields and values to filter the count

        Returns:
            Number of entities matching the criteria
        """
        pass

    @abstractmethod
    async def find_by_ids(self, entity_ids: List[int]) -> List[T]:
        """
        Finds entities by a list of IDs.

        Args:
            entity_ids: List of IDs to search for

        Returns:
            List of entities found
        """
        pass

    @abstractmethod
    async def delete_by_ids(self, entity_ids: List[int]) -> bool:
        """
        Deletes entities by a list of IDs.

        Args:
            entity_ids: List of IDs to delete

        Returns:
            True if all entities were deleted, False if some were not found
        """
        pass

    @abstractmethod
    async def update_by_id(
        self, entity_id: int, update_data: Dict[str, Any]
    ) -> T | None:
        """
        Updates an entity by its ID with the provided data.

        Args:
            entity_id: ID of the entity to update
            update_data: Dictionary with fields and values to update

        Returns:
            The updated entity or None if not found
        """
        pass

    @abstractmethod
    async def update_all_by(
        self, filters: Dict[str, Any], update_data: Dict[str, Any]
    ) -> int:
        """
        Updates all entities matching the filters.

        Args:
            filters: Dictionary with fields and values to filter entities
            update_data: Dictionary with fields and values to update

        Returns:
            Number of entities updated
        """
        pass

    @abstractmethod
    async def get_pageable(
        self,
        page: int,
        size: int,
        join_models: List[SQLModel] = None,
        where_conditions: Dict[str, Any] = None,
    ) -> Page:
        """
        Gets a page of entities with pagination metadata.

        Args:
            page: Page number (starting from 1)
            size: Page size
            join_models: Optional list of models to JOIN with
            where_conditions: Additional WHERE conditions

        Returns:
            Page object with data and pagination metadata
        """
        pass

    @abstractmethod
    async def get_pageable_by(
        self,
        page: int,
        size: int,
        join_models: List[SQLModel] = None,
        where_conditions: Dict[str, Any] = None,
        **kwargs,
    ) -> Page:
        """
        Gets a page of filtered entities with pagination metadata.

        Args:
            page: Page number (starting from 1)
            size: Page size
            join_models: Optional list of models to JOIN with
            where_conditions: Additional WHERE conditions
            **kwargs: Fields and values to filter entities

        Returns:
            Page object with filtered data and pagination metadata
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def save_or_update(self, entity: T) -> T:
        """
        Saves a new entity or updates an existing one.

        Args:
            entity: The entity to save or update

        Returns:
            The saved or updated entity
        """
        pass

    @abstractmethod
    async def find_all_ordered_by(
        self,
        order_field: str,
        ascending: bool = True,
        join_models: List[SQLModel] = None,
        where_conditions: Dict[str, Any] = None,
        **kwargs,
    ) -> List[T]:
        """
        Finds all entities ordered by a specific field.

        Args:
            order_field: Field name to order by
            ascending: True for ascending order, False for descending
            join_models: Optional list of models to JOIN with
            where_conditions: Additional WHERE conditions
            **kwargs: Fields and values for search

        Returns:
            List of entities ordered by the specified field
        """
        pass

    @abstractmethod
    async def find_first_ordered_by(
        self, order_field: str, ascending: bool = True, **kwargs
    ) -> T | None:
        """
        Finds the first entity when ordered by a specific field.

        Args:
            order_field: Field name to order by
            ascending: True for ascending order, False for descending
            **kwargs: Fields and values for search

        Returns:
            The first entity or None if not found
        """
        pass

    @abstractmethod
    async def find_last_ordered_by(
        self, order_field: str, ascending: bool = True, **kwargs
    ) -> T | None:
        """
        Finds the last entity when ordered by a specific field.

        Args:
            order_field: Field name to order by
            ascending: True for ascending order, False for descending
            **kwargs: Fields and values for search

        Returns:
            The last entity or None if not found
        """
        pass

    @abstractmethod
    async def exists_by_id(self, entity_id: int) -> bool:
        """
        Checks if an entity exists by its ID.

        Args:
            entity_id: ID to check

        Returns:
            True if entity exists, False otherwise
        """
        pass

    @abstractmethod
    async def find_all_in_range(
        self, field_name: str, min_value: Any, max_value: Any
    ) -> List[T]:
        """
        Finds all entities where a field value is within a range.

        Args:
            field_name: Field name to check
            min_value: Minimum value (inclusive)
            max_value: Maximum value (inclusive)

        Returns:
            List of entities within the range
        """
        pass

    @abstractmethod
    async def find_all_like(self, field_name: str, pattern: str) -> List[T]:
        """
        Finds all entities where a field matches a pattern (LIKE operation).

        Args:
            field_name: Field name to search
            pattern: Pattern to match (supports SQL LIKE wildcards)

        Returns:
            List of entities matching the pattern
        """
        pass

    @abstractmethod
    async def find_all_in_list(self, field_name: str, values: List[Any]) -> List[T]:
        """
        Finds all entities where a field value is in a list of values.

        Args:
            field_name: Field name to check
            values: List of values to match

        Returns:
            List of entities with field values in the list
        """
        pass

    @abstractmethod
    async def find_all_not_in_list(self, field_name: str, values: List[Any]) -> List[T]:
        """
        Finds all entities where a field value is NOT in a list of values.

        Args:
            field_name: Field name to check
            values: List of values to exclude

        Returns:
            List of entities with field values not in the list
        """
        pass

    @abstractmethod
    async def get_distinct_values(self, field_name: str) -> List[Any]:
        """
        Gets all distinct values for a specific field.

        Args:
            field_name: Field name to get distinct values from

        Returns:
            List of distinct values
        """
        pass

    @abstractmethod
    async def find_all_greater_than(self, field_name: str, value: Any) -> List[T]:
        """
        Finds all entities where a field value is greater than a given value.

        Args:
            field_name: Field name to compare
            value: Value to compare against

        Returns:
            List of entities with field values greater than the given value
        """
        pass

    @abstractmethod
    async def find_all_less_than(self, field_name: str, value: Any) -> List[T]:
        """
        Finds all entities where a field value is less than a given value.

        Args:
            field_name: Field name to compare
            value: Value to compare against

        Returns:
            List of entities with field values less than the given value
        """
        pass

    @abstractmethod
    async def find_all_between_dates(
        self, field_name: str, start_date: Any, end_date: Any
    ) -> List[T]:
        """
        Finds all entities where a date field is between two dates.

        Args:
            field_name: Date field name to check
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of entities with dates between the range
        """
        pass

    @abstractmethod
    async def soft_delete_by_id(
        self, entity_id: int, deleted_field: str = "deleted"
    ) -> bool:
        """
        Performs a soft delete by setting a deleted flag.

        Args:
            entity_id: ID of the entity to soft delete
            deleted_field: Name of the field to mark as deleted

        Returns:
            True if soft deleted successfully, False if not found
        """
        pass

    @abstractmethod
    async def restore_by_id(
        self, entity_id: int, deleted_field: str = "deleted"
    ) -> bool:
        """
        Restores a soft-deleted entity by unsetting the deleted flag.

        Args:
            entity_id: ID of the entity to restore
            deleted_field: Name of the field to unmark as deleted

        Returns:
            True if restored successfully, False if not found
        """
        pass

    @abstractmethod
    async def find_all_active(self, active_field: str = "active") -> List[T]:
        """
        Finds all active entities based on an active flag.

        Args:
            active_field: Name of the field that indicates active status

        Returns:
            List of active entities
        """
        pass

    @abstractmethod
    async def find_all_inactive(self, active_field: str = "active") -> List[T]:
        """
        Finds all inactive entities based on an active flag.

        Args:
            active_field: Name of the field that indicates active status

        Returns:
            List of inactive entities
        """
        pass

    @abstractmethod
    async def bulk_update_field(
        self, entity_ids: List[int], field_name: str, new_value: Any
    ) -> int:
        """
        Updates a specific field for multiple entities by their IDs.

        Args:
            entity_ids: List of entity IDs to update
            field_name: Name of the field to update
            new_value: New value to set

        Returns:
            Number of entities updated
        """
        pass

    @abstractmethod
    async def find_random(self, limit: int = 1) -> List[T]:
        """
        Finds random entities from the table.

        Args:
            limit: Maximum number of random entities to return

        Returns:
            List of random entities
        """
        pass
