from enum import Enum


class JoinType(Enum):
    """
    Supported JOIN types for SQLModel queries.
    
    INNER: Default JOIN type (INNER JOIN)
    LEFT_OUTER: LEFT OUTER JOIN using isouter=True
    """
    INNER = "inner"
    LEFT_OUTER = "left_outer"