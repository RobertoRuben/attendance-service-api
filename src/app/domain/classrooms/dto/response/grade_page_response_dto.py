from src.app.core.model.page import Page
from src.app.domain.classrooms.dto.response import GradeResponseDTO


class GradePageResponseDTO(Page):
    """
    DTO for paginated responses containing grade information.

    Args:
        Page (Page): The base pagination class.
    """

    data: list[GradeResponseDTO]
