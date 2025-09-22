from src.app.core.model import Page
from .user_response_dto import UserResponseDTO


class UserPageResponseDTO(Page):
    """Paginated response for users.

    Container for paginated user responses. Extends the base Page class and
    includes a list of UserResponseDTO items and pagination metadata.

    Attributes:
        data (list[UserResponseDTO]): List of users on the current page.
            Each element follows the structure defined by UserResponseDTO.
        meta (src.app.core.model.pagination.Pagination): Pagination metadata
            provided by the base Page class. Typically includes fields such as
            page (current page number), size (page size) and total (total items).

    Example:
        >>> page = UserPageResponseDTO(
        ...     data=[UserResponseDTO(id=1, username="jdoe", ...)],
        ...     meta=Pagination(page=1, size=10, total=42)
        ... )
    """

    data: list[UserResponseDTO]
