from src.app.core.model import Page
from ..response import SectionResponseDTO


class SectionPageResponseDTO(Page):
    """
    DTO for paginated response containing a list of sections.

    Args:
        data: List of section data transfer objects.
    """

    data: list[SectionResponseDTO]
