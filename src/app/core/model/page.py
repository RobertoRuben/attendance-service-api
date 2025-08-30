from pydantic import BaseModel
from typing import Any
from .pageable import Pageable


class Page(BaseModel):
    data: list[Any]
    meta: Pageable
