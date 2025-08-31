from .grade_controller import router as grade_router, grades_tags_metadata
from .section_controller import router as section_router, sections_tags_metadata

__all__ = [
    "grade_router",
    "grades_tags_metadata",
    "section_router",
    "sections_tags_metadata",
]
