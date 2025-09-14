import math

from src.app.core.db.decorator import transactional
from src.app.core.model import Page, Pagination
from src.app.core.repository.implementation import (
    BaseRepository,
)
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.domain.classrooms.model import Grade, Section
from src.app.domain.students.model import Student
from src.app.domain.students.repository.interface import (
    IStudentRepository,
)


class StudentRepositoryImpl(BaseRepository[Student], IStudentRepository):
    """Repository implementation for Student entity.

    Provides data access methods for students. This implementation includes a
    paginated query that joins Grade and Section to return only the fields
    required by clients (including grade_name and section_name).

    Note:
        Uses SQLModel / SQLAlchemy async session provided by the base repository.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with async session.

        Args:
            session (AsyncSession): Async SQLAlchemy session bound to a transaction.
        """
        super().__init__(session=session, entity_class=Student)

    @transactional(readonly=True)
    async def get_pageable_students(
        self,
        page: int,
        size: int,
    ) -> Page:
        """Return a paginated list of students including grade and section names.

        The method performs JOINs with Grade and Section but selects only the
        necessary columns (student fields plus grade_name and section_name)
        to be efficient.

        Args:
            page (int): 1-based page number.
            size (int): Number of items per page.

        Returns:
            Page: Paginated result containing a list of student dicts. Each dict
                  includes keys: id, dni, names, paternal_surname,
                  maternal_surname, grade_id, grade_name, section_id,
                  section_name, created_at, updated_at.

        Raises:
            Any exception raised by the underlying database/session will bubble up.
        """
        offset_value = (page - 1) * size
        stmt = (
            select(
                Student.id,
                Student.dni,
                Student.names,
                Student.paternal_surname,
                Student.maternal_surname,
                Student.grade_id,
                Grade.grade_name,
                Student.section_id,
                Section.section_name,
                Student.created_at,
                Student.updated_at,
            )
            .join(Grade, Student.grade_id == Grade.id)
            .join(Section, Student.section_id == Section.id)
            .order_by(Student.id)
        )

        stmt = stmt.offset(offset_value).limit(size)
        result = await self.session.exec(stmt)
        students_data = [dict(row._mapping) for row in result]

        count_stmt = select(func.count(Student.id))
        count_result = await self.session.exec(count_stmt)
        total_items = count_result.first()

        total_pages = math.ceil(total_items / size) if total_items > 0 else 1
        next_page = page + 1 if page < total_pages else None
        previous_page = page - 1 if page > 1 else None

        page_info = Pagination(
            current_page=page,
            per_page=size,
            total=total_items,
            total_pages=total_pages,
            next_page=next_page,
            previous_page=previous_page,
        )

        return Page(
            data=students_data,
            page_info=page_info,
        )
