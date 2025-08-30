from typing import Any, Dict, List, Type, TypeVar
from sqlmodel import SQLModel, func, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.db.decorator import transactional
from src.app.core.exception import InvalidFieldException
from src.app.core.repository.enum import JoinType

T = TypeVar("T", bound=SQLModel)


class RepositoryHelpers:
    """
    Helper class for repository operations.
    Contains utilities for validation, search, and data manipulation.
    """

    @staticmethod
    def validate_fields(entity_class: Type[T], fields: Dict[str, Any]) -> None:
        """
        Validates that fields exist in the model.

        Args:
            entity_class: Model class
            fields: Dictionary with fields and values to validate

        Raises:
            InvalidFieldException: If any field does not exist in the model
        """
        valid_fields = {
            attr
            for attr in dir(entity_class)
            if not attr.startswith("_") and hasattr(entity_class, attr)
        }

        for key in fields.keys():
            if key not in valid_fields:
                raise InvalidFieldException(
                    message=f"Field '{key}' does not exist in the {entity_class.__name__} model",
                    details=f"Valid fields are: {', '.join(sorted(valid_fields))}",
                )

    @staticmethod
    def apply_joins(
        stmt, join_models: List[SQLModel] = None, join_type: JoinType = JoinType.INNER
    ):
        """
        Applies optional JOINs to the statement.

        Args:
            stmt: Base statement
            join_models: List of models to JOIN with
            join_type: JOIN type (INNER by default, LEFT_OUTER)

        Returns:
            Statement with JOINs applied
        """
        if join_models:
            for model in join_models:
                if join_type == JoinType.LEFT_OUTER:
                    stmt = stmt.join(model, isouter=True)
                else:  # JoinType.INNER (default)
                    stmt = stmt.join(model)
        return stmt

    @staticmethod
    def apply_where_conditions(
        stmt, entity_class: Type[T], where_conditions: Dict[str, Any] = None
    ):
        """
        Applies additional WHERE conditions to the statement.

        Args:
            stmt: Base statement
            entity_class: Model class
            where_conditions: Dictionary with additional WHERE conditions

        Returns:
            Statement with WHERE conditions applied
        """
        if where_conditions:
            RepositoryHelpers.validate_fields(entity_class, where_conditions)
            for key, value in where_conditions.items():
                if isinstance(value, list):
                    # For IN conditions
                    stmt = stmt.where(getattr(entity_class, key).in_(value))
                elif isinstance(value, dict):
                    # For complex conditions like range, like, etc.
                    field_attr = getattr(entity_class, key)
                    if "gt" in value:
                        stmt = stmt.where(field_attr > value["gt"])
                    if "gte" in value:
                        stmt = stmt.where(field_attr >= value["gte"])
                    if "lt" in value:
                        stmt = stmt.where(field_attr < value["lt"])
                    if "lte" in value:
                        stmt = stmt.where(field_attr <= value["lte"])
                    if "like" in value:
                        stmt = stmt.where(field_attr.like(value["like"]))
                    if "ne" in value:  # not equal
                        stmt = stmt.where(field_attr != value["ne"])
                else:
                    # Simple equality condition
                    stmt = stmt.where(getattr(entity_class, key) == value)
        return stmt

    @staticmethod
    @transactional(readonly=True)
    async def find_all_ordered_by(
        session: AsyncSession,
        entity_class: Type[T],
        order_field: str,
        ascending: bool = True,
        **kwargs,
    ) -> List[T]:
        """
        Finds all entities ordered by a specific field.

        Args:
            session: Database session
            entity_class: Model class
            order_field: Field to order by
            ascending: If True orders ascending, if False descending
            **kwargs: Additional filters

        Returns:
            List of ordered entities

        Raises:
            InvalidFieldException: If the order field does not exist in the model
        """
        RepositoryHelpers.validate_fields(entity_class, {order_field: None, **kwargs})

        stmt = select(entity_class)

        # Apply filters
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(entity_class, key) == value)

        # Apply ordering
        order_attr = getattr(entity_class, order_field)
        if ascending:
            stmt = stmt.order_by(order_attr)
        else:
            stmt = stmt.order_by(order_attr.desc())

        results = await session.exec(stmt)
        return list(results.all())

    @staticmethod
    @transactional(readonly=True)
    async def find_first_ordered_by(
        session: AsyncSession,
        entity_class: Type[T],
        order_field: str,
        ascending: bool = True,
        **kwargs,
    ) -> T | None:
        """
        Finds the first entity ordered by a specific field.

        Args:
            session: Database session
            entity_class: Model class
            order_field: Field to order by
            ascending: If True orders ascending, if False descending
            **kwargs: Additional filters

        Returns:
            The first entity found or None

        Raises:
            InvalidFieldException: If the order field does not exist in the model
        """
        entities = await RepositoryHelpers.find_all_ordered_by(
            session, entity_class, order_field, ascending, **kwargs
        )
        return entities[0] if entities else None

    @staticmethod
    @transactional(readonly=True)
    async def find_last_ordered_by(
        session: AsyncSession,
        entity_class: Type[T],
        order_field: str,
        ascending: bool = True,
        **kwargs,
    ) -> T | None:
        """
        Finds the last entity ordered by a specific field.

        Args:
            session: Database session
            entity_class: Model class
            order_field: Field to order by
            ascending: If True orders ascending, if False descending
            **kwargs: Additional filters

        Returns:
            The last entity found or None

        Raises:
            InvalidFieldException: If the order field does not exist in the model
        """
        entities = await RepositoryHelpers.find_all_ordered_by(
            session, entity_class, order_field, not ascending, **kwargs
        )
        return entities[0] if entities else None

    @staticmethod
    @transactional(readonly=True)
    async def find_all_in_range(
        session: AsyncSession,
        entity_class: Type[T],
        field_name: str,
        min_value: Any,
        max_value: Any,
    ) -> List[T]:
        """
        Finds all entities where a field is within a specific range.

        Args:
            session: Database session
            entity_class: Model class
            field_name: Field name
            min_value: Minimum value (inclusive)
            max_value: Maximum value (inclusive)

        Returns:
            List of entities within the range

        Raises:
            InvalidFieldException: If the field does not exist in the model
        """
        RepositoryHelpers.validate_fields(entity_class, {field_name: None})

        field_attr = getattr(entity_class, field_name)
        stmt = (
            select(entity_class)
            .where((field_attr >= min_value) & (field_attr <= max_value))
            .order_by(entity_class.id)
        )

        results = await session.exec(stmt)
        return list(results.all())

    @staticmethod
    @transactional(readonly=True)
    async def find_all_like(
        session: AsyncSession, entity_class: Type[T], field_name: str, pattern: str
    ) -> List[T]:
        """
        Finds all entities where a field matches a LIKE pattern.

        Args:
            session: Database session
            entity_class: Model class
            field_name: Text field name
            pattern: LIKE pattern (e.g., '%text%')

        Returns:
            List of entities matching the pattern

        Raises:
            InvalidFieldException: If the field does not exist in the model
        """
        RepositoryHelpers.validate_fields(entity_class, {field_name: None})

        field_attr = getattr(entity_class, field_name)
        stmt = (
            select(entity_class)
            .where(field_attr.like(pattern))
            .order_by(entity_class.id)
        )

        results = await session.exec(stmt)
        return list(results.all())

    @staticmethod
    @transactional(readonly=True)
    async def find_all_in_list(
        session: AsyncSession,
        entity_class: Type[T],
        field_name: str,
        values: List[Any],
    ) -> List[T]:
        """
        Finds all entities where a field is in a list of values.

        Args:
            session: Database session
            entity_class: Model class
            field_name: Field name
            values: List of allowed values

        Returns:
            List of matching entities

        Raises:
            InvalidFieldException: If the field does not exist in the model
        """
        if not values:
            return []

        RepositoryHelpers.validate_fields(entity_class, {field_name: None})

        field_attr = getattr(entity_class, field_name)
        stmt = (
            select(entity_class).where(field_attr.in_(values)).order_by(entity_class.id)
        )

        results = await session.exec(stmt)
        return list(results.all())

    @staticmethod
    @transactional(readonly=True)
    async def find_all_not_in_list(
        session: AsyncSession,
        entity_class: Type[T],
        field_name: str,
        values: List[Any],
    ) -> List[T]:
        """
        Finds all entities where a field is NOT in a list of values.

        Args:
            session: Database session
            entity_class: Model class
            field_name: Field name
            values: List of excluded values

        Returns:
            List of entities that do NOT match

        Raises:
            InvalidFieldException: If the field does not exist in the model
        """
        if not values:
            # If no values to exclude, return all entities
            stmt = select(entity_class).order_by(entity_class.id)
            results = await session.exec(stmt)
            return list(results.all())

        RepositoryHelpers.validate_fields(entity_class, {field_name: None})

        field_attr = getattr(entity_class, field_name)
        stmt = (
            select(entity_class)
            .where(~field_attr.in_(values))
            .order_by(entity_class.id)
        )

        results = await session.exec(stmt)
        return list(results.all())

    @staticmethod
    @transactional(readonly=True)
    async def get_distinct_values(
        session: AsyncSession, entity_class: Type[T], field_name: str
    ) -> List[Any]:
        """
        Gets all unique values from a specific field.

        Args:
            session: Database session
            entity_class: Model class
            field_name: Field name

        Returns:
            List of unique values

        Raises:
            InvalidFieldException: If the field does not exist in the model
        """
        RepositoryHelpers.validate_fields(entity_class, {field_name: None})

        field_attr = getattr(entity_class, field_name)
        stmt = select(field_attr).distinct().order_by(field_attr)

        results = await session.exec(stmt)
        return [value for value in results.all() if value is not None]

    @staticmethod
    @transactional(readonly=True)
    async def find_all_greater_than(
        session: AsyncSession, entity_class: Type[T], field_name: str, value: Any
    ) -> List[T]:
        """
        Finds all entities where a field is greater than a value.

        Args:
            session: Database session
            entity_class: Model class
            field_name: Field name
            value: Comparison value

        Returns:
            List of entities where the field is greater

        Raises:
            InvalidFieldException: If the field does not exist in the model
        """
        RepositoryHelpers.validate_fields(entity_class, {field_name: None})

        field_attr = getattr(entity_class, field_name)
        stmt = select(entity_class).where(field_attr > value).order_by(entity_class.id)

        results = await session.exec(stmt)
        return list(results.all())

    @staticmethod
    @transactional(readonly=True)
    async def find_all_less_than(
        session: AsyncSession, entity_class: Type[T], field_name: str, value: Any
    ) -> List[T]:
        """
        Finds all entities where a field is less than a value.

        Args:
            session: Database session
            entity_class: Model class
            field_name: Field name
            value: Comparison value

        Returns:
            List of entities where the field is less

        Raises:
            InvalidFieldException: If the field does not exist in the model
        """
        RepositoryHelpers.validate_fields(entity_class, {field_name: None})

        field_attr = getattr(entity_class, field_name)
        stmt = select(entity_class).where(field_attr < value).order_by(entity_class.id)

        results = await session.exec(stmt)
        return list(results.all())

    @staticmethod
    @transactional(readonly=True)
    async def find_all_between_dates(
        session: AsyncSession,
        entity_class: Type[T],
        field_name: str,
        start_date: Any,
        end_date: Any,
    ) -> List[T]:
        """
        Finds all entities where a date field is between two dates.

        Args:
            session: Database session
            entity_class: Model class
            field_name: Date field name
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of entities within the date range

        Raises:
            InvalidFieldException: If the field does not exist in the model
        """
        return await RepositoryHelpers.find_all_in_range(
            session, entity_class, field_name, start_date, end_date
        )

    @staticmethod
    @transactional(readonly=False)
    async def soft_delete_by_id(
        session: AsyncSession,
        entity_class: Type[T],
        entity_id: int,
        deleted_field: str = "deleted",
    ) -> bool:
        """
        Marks an entity as deleted (soft delete) instead of physically deleting it.

        Args:
            session: Database session
            entity_class: Model class
            entity_id: Entity ID
            deleted_field: Name of the field that marks as deleted

        Returns:
            True if marked as deleted, False if not found

        Raises:
            InvalidFieldException: If the field does not exist in the model
        """
        RepositoryHelpers.validate_fields(entity_class, {deleted_field: None})

        stmt = select(entity_class).where(entity_class.id == entity_id)
        results = await session.exec(stmt)
        entity = results.first()

        if entity:
            setattr(entity, deleted_field, True)
            await session.flush()
            return True
        return False

    @staticmethod
    @transactional(readonly=False)
    async def restore_by_id(
        session: AsyncSession,
        entity_class: Type[T],
        entity_id: int,
        deleted_field: str = "deleted",
    ) -> bool:
        """
        Restores an entity marked as deleted (soft delete).

        Args:
            session: Database session
            entity_class: Model class
            entity_id: Entity ID
            deleted_field: Name of the field that marks as deleted

        Returns:
            True if restored, False if not found

        Raises:
            InvalidFieldException: If the field does not exist in the model
        """
        RepositoryHelpers.validate_fields(entity_class, {deleted_field: None})

        stmt = select(entity_class).where(entity_class.id == entity_id)
        results = await session.exec(stmt)
        entity = results.first()

        if entity:
            setattr(entity, deleted_field, False)
            await session.flush()
            return True
        return False

    @staticmethod
    @transactional(readonly=False)
    async def bulk_update_field(
        session: AsyncSession,
        entity_class: Type[T],
        entity_ids: List[int],
        field_name: str,
        new_value: Any,
    ) -> int:
        """
        Updates a specific field for multiple entities.

        Args:
            session: Database session
            entity_class: Model class
            entity_ids: List of entity IDs to update
            field_name: Name of the field to update
            new_value: New value for the field

        Returns:
            Number of entities updated

        Raises:
            InvalidFieldException: If the field does not exist in the model
        """
        if not entity_ids:
            return 0

        RepositoryHelpers.validate_fields(entity_class, {field_name: None})

        stmt = (
            update(entity_class)
            .where(entity_class.id.in_(entity_ids))
            .values(**{field_name: new_value})
        )

        result = await session.exec(stmt)
        return result.rowcount

    @staticmethod
    @transactional(readonly=True)
    async def find_random(
        session: AsyncSession, entity_class: Type[T], limit: int = 1
    ) -> List[T]:
        """
        Finds random entities.

        Args:
            session: Database session
            entity_class: Model class
            limit: Maximum number of entities to return

        Returns:
            List of random entities
        """
        # Use different approaches depending on the database
        stmt = select(entity_class).order_by(func.random()).limit(limit)

        results = await session.exec(stmt)
        return list(results.all())
