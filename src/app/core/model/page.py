from typing import Any

from pydantic import BaseModel

from .pagination import Pagination


class Page(BaseModel):
    data: list[Any]
    meta: Pagination
