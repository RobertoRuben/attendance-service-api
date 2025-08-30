from pydantic import BaseModel


class Pageable(BaseModel):
    current_page: int
    per_page: int
    total: int
    total_pages: int
    next_page: int | None = None
    previous_page: int | None = None
