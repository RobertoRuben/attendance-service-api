import functools
import inspect
import textwrap
import time
import asyncio
import re
from typing import Callable, Any, Literal, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from src.app.core.exception import DatabaseException

T = TypeVar("T")

DANGEROUS_SQL_PATTERNS = {
    r"\b(DROP|ALTER|CREATE|TRUNCATE|DELETE|INSERT|UPDATE)\s+(?!.*WHERE)",  # DDL/DML without WHERE
    r";\s*DROP\s+",  # Classic SQL injection
    r"--\s*",  # SQL comment
    r"/\*.*\*/",  # Block comments
    r"\b(EXEC|EXECUTE|SP_|XP_)\s*\(",  # Stored procedures
    r"\b(UNION\s+SELECT|UNION\s+ALL\s+SELECT)",  # UNION attacks
    r"@@\w+",  # System variables
}

COMPILED_PATTERNS = [
    re.compile(pattern, re.IGNORECASE) for pattern in DANGEROUS_SQL_PATTERNS
]


def query(
    sql: str,
    *,
    fetch: Literal["all", "one", "scalar", "none"] = "all",
    model: type | None = None,
    log_level: str | None = None,
    timeout: int | None = None,
    allow_dangerous: bool = False,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to run raw SQL queries in repository/service methods using AsyncSession.

    SECURITY NOTES:
    - Uses parameterized queries to prevent basic SQL injection
    - Validates SQL for dangerous patterns (can be disabled with allow_dangerous=True)
    - Does NOT prevent all injection vectors (dynamic table/column names, etc.)
    - Always validate and sanitize dynamic SQL components manually

    :param sql: Raw SQL string. Use named parameters (e.g., :id) matching the function signature.
    :param fetch: Cursor mode: "all" (default), "one", "scalar" (first column), or "none" (no result).
    :param model: Optional class (e.g., SQLModel, Pydantic) to map rows to objects.
    :param log_level: "DEBUG", "INFO" or None (silent).
    :param timeout: Max time in seconds before timing out the query.
    :param allow_dangerous: Skip dangerous SQL pattern validation (use with caution).
    :return: Depends on `fetch`:
        • "all" → list[Row | model]
        • "one" → Row | model
        • "scalar" → Any
        • "none" → None
    :raises DatabaseException: On SQL execution failure, timeout, or security validation.
    """
    sql_clean = textwrap.dedent(sql).strip()

    if not allow_dangerous:
        _validate_sql_security(sql_clean)

    sql_obj = text(sql_clean)

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        sig = inspect.signature(fn)

        _validate_sql_parameters(sql_clean, sig)

        @functools.wraps(fn)
        async def wrapper(self, *args: Any, **kwargs: Any):
            bound = sig.bind(self, *args, **kwargs)
            bound.apply_defaults()
            params = {k: v for k, v in bound.arguments.items() if k != "self"}

            _validate_parameter_values(params)

            session: AsyncSession = getattr(self, "session", None)
            if not isinstance(session, AsyncSession):
                raise RuntimeError("query(): 'self.session' must be an AsyncSession")

            def _log(msg: str, lvl: str = "DEBUG"):
                if log_level == "DEBUG" or (log_level == "INFO" and lvl != "DEBUG"):
                    print(msg)

            async def _execute() -> AsyncResult:
                start = time.perf_counter()
                try:
                    result = await session.execute(sql_obj, params)
                    _log(
                        f"[QUERY] ⏱  {sql_obj.text.split()[0]} in {time.perf_counter() - start:.4f}s",
                        "DEBUG",
                    )
                    return result
                except SQLAlchemyError as exc:
                    raise DatabaseException(
                        message="Native SQL error",
                        details=str(exc),
                        instance=f"{self.__class__.__name__}.{fn.__name__}",
                    ) from exc

            if timeout:
                try:
                    result = await asyncio.wait_for(_execute(), timeout)
                except asyncio.TimeoutError as exc:
                    raise DatabaseException(
                        message="Query timeout",
                        details=f"Exceeded {timeout}s",
                        instance=f"{self.__class__.__name__}.{fn.__name__}",
                    ) from exc
            else:
                result = await _execute()

            if fetch == "none":
                return None
            if fetch == "scalar":
                return result.scalar()
            if fetch == "one":
                row = result.fetchone()
                return _map_row(row, model) if model and row else row

            rows = result.fetchall()
            return [_map_row(r, model) for r in rows] if model else rows

        return wrapper

    return decorator


def _validate_sql_security(sql: str) -> None:
    """
    Perform basic SQL security validation to detect potentially dangerous patterns.

    :param sql: SQL string to validate
    :raises DatabaseException: If dangerous patterns are detected
    """
    for pattern in COMPILED_PATTERNS:
        if pattern.search(sql):
            raise DatabaseException(
                message="Potentially dangerous SQL pattern detected",
                details=f"Pattern matched: {pattern.pattern}",
                instance="SQL Security Validation",
            )


def _validate_sql_parameters(sql: str, signature: inspect.Signature) -> None:
    """
    Validate that all SQL named parameters have corresponding function parameters.

    :param sql: SQL string with named parameters
    :param signature: Function signature to check against
    :raises DatabaseException: If parameters don't match
    """
    sql_params = set(re.findall(r":(\w+)", sql))

    func_params = set(signature.parameters.keys()) - {"self"}

    missing_params = sql_params - func_params
    if missing_params:
        raise DatabaseException(
            message="SQL parameters missing from function signature",
            details=f"Missing parameters: {', '.join(missing_params)}",
            instance="SQL Parameter Validation",
        )


def _validate_parameter_values(params: dict) -> None:
    """
    Validate parameter values for common injection patterns.

    :param params: Dictionary of parameter values
    :raises DatabaseException: If suspicious values are detected
    """
    for param_name, value in params.items():
        if isinstance(value, str):
            for pattern in COMPILED_PATTERNS:
                if pattern.search(value):
                    raise DatabaseException(
                        message="Suspicious SQL pattern in parameter value",
                        details=f"Parameter '{param_name}' contains potential injection",
                        instance="Parameter Value Validation",
                    )


def _has_from_attributes_config(model) -> bool:
    """
    Check if a Pydantic/SQLModel has from_attributes=True configuration.
    Supports both Pydantic v1 and v2 configurations.
    """
    # Check Pydantic v2 ConfigDict
    model_config = getattr(model, "model_config", None)
    if model_config:
        if hasattr(model_config, "get") and callable(model_config.get):
            return model_config.get("from_attributes", False)
        elif hasattr(model_config, "from_attributes"):
            return model_config.from_attributes
        elif isinstance(model_config, dict):
            return model_config.get("from_attributes", False)

    # Check Pydantic v1 Config class
    config_class = getattr(model, "Config", None)
    if config_class and hasattr(config_class, "from_attributes"):
        return getattr(config_class, "from_attributes", False)

    # Check legacy Pydantic v1 orm_mode
    if config_class and hasattr(config_class, "orm_mode"):
        return getattr(config_class, "orm_mode", False)

    return False


def _map_row(row, model):
    """
    Map a SQLAlchemy Row to a given model using column-to-field matching.

    Automatically detects if the model has from_attributes=True configuration
    and uses the appropriate validation method for optimal performance.
    """
    if model is None:
        return row

    # Check if model has model_validate (Pydantic v2/SQLModel)
    if hasattr(model, "model_validate"):
        from_attributes = _has_from_attributes_config(model)

        if from_attributes:
            # Use the row directly - Pydantic will extract attributes
            return model.model_validate(row)
        else:
            # Convert to dict first for models without from_attributes
            data = {key: row[key] for key in row._mapping.keys()}
            return model.model_validate(data)

    # Fallback for older Pydantic or other models
    data = {key: row[key] for key in row._mapping.keys()}
    return model(**data)
