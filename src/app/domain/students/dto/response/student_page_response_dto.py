from src.app.core.model import Page
from ..response import StudentResponseDTO


class StudentPageResponseDTO(Page):
    """Paginated response DTO for students (Google style docstring).

    A container for a paginated list of StudentResponseDTO objects together
    with pagination metadata inherited from `Page`.

    Args:
        data (list[StudentResponseDTO]): List of students for the current page.
        meta (Pagination): Pagination metadata (current_page, per_page, total, total_pages, ...).

    Attributes:
        data (list[StudentResponseDTO]): Students returned on this page.
        meta (Pagination): Pagination information for the result set.
    """

    data: list[StudentResponseDTO]
