import math

from sqlmodel import func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.db.decorator import transactional
from src.app.core.model import Page, Pagination
from src.app.core.repository.implementation import (
    BaseRepository,
)
from src.app.domain.classrooms.model import Grade, Section
from src.app.domain.students.model import Student
from src.app.domain.students.repository.interface import (
    IStudentRepository,
)


class StudentRepositoryImpl(BaseRepository[Student], IStudentRepository):
    """Repository implementation for Student entity.

    Provides data access methods for students with optimized queries that join
    related entities (Grade and Section) while selecting only required fields
    for efficient data transfer to clients.

    This implementation uses SQLModel/SQLAlchemy async sessions and includes
    transactional decorators for proper transaction management.

    Attributes:
        session (AsyncSession): The async SQLAlchemy session for database operations.
        entity_class (type): The Student model class inherited from BaseRepository.

    Note:
        All methods use readonly transactions where appropriate to optimize
        database performance and ensure data consistency.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the student repository with an async database session.

        Args:
            session (AsyncSession): Async SQLAlchemy session bound to a database
                transaction. This session will be used for all database operations
                within this repository instance.

        Note:
            The session should be properly configured with appropriate connection
            pooling and transaction isolation level before being passed to this
            constructor.
        """
        super().__init__(session=session, entity_class=Student)

    @transactional(readonly=True)
    async def get_pageable_students(
        self,
        page: int,
        size: int,
    ) -> Page:
        """Retrieve a paginated list of students with grade and section information.

        Executes an optimized query that performs JOINs with Grade and Section
        tables but selects only the necessary columns to minimize data transfer
        and improve performance. The result includes both student data and
        related grade/section names.

        Args:
            page (int): The 1-based page number to retrieve. Must be greater than 0.
                For example, page=1 retrieves the first set of results.
            size (int): The number of student records to include per page.
                Must be greater than 0. Typically ranges from 10-100 for
                optimal performance.

        Returns:
            Page: A paginated response containing:
                - data (List[Dict]): List of student dictionaries, each containing:
                    * id: Student's unique identifier
                    * dni: Student's national identification number
                    * names: Student's first and middle names
                    * paternal_surname: Student's paternal surname
                    * maternal_surname: Student's maternal surname
                    * grade_id: Foreign key reference to grade
                    * grade_name: Name of the grade (from joined Grade table)
                    * section_id: Foreign key reference to section
                    * section_name: Name of the section (from joined Section table)
                    * created_at: Timestamp when student record was created
                    * updated_at: Timestamp when student record was last modified
                - page_info (Pagination): Pagination metadata containing current page,
                    total items, total pages, and navigation links.

        Raises:
            ValueError: If page or size parameters are less than or equal to 0.
            SQLAlchemyError: If there's a database connection or query execution error.
            TransactionError: If the database transaction fails or is rolled back.

        Note:
            Results are ordered by student ID to ensure consistent pagination
            across multiple requests. The method uses efficient SQL JOINs to
            avoid N+1 query problems.
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
            .offset(offset_value)
            .limit(size)
        )

        result = await self.session.exec(stmt)

        students_data = [dict(row._mapping) for row in result]


        count_stmt = select(func.count(Student.id))
        count_result = await self.session.exec(count_stmt)
        total_items = count_result.first()

        total_pages = math.ceil(total_items / size) if total_items > 0 else 1
        next_page = page + 1 if page < total_pages else None
        previous_page = page - 1 if page > 1 else None

        return Page(
            data=students_data,
            meta=Pagination(
                current_page=page,
                per_page=size,
                total=total_items,
                total_pages=total_pages,
                next_page=next_page,
                previous_page=previous_page,
            ),
        )

    @transactional(readonly=True)
    async def find(self, page: int, size: int, search_query: str) -> Page:
        """Search for students across multiple fields with global text matching.

        Performs a flexible search that looks for matches in student DNI (exact match)
        and names (partial match) fields. When no search query is provided, returns
        all students with pagination. The search is case-insensitive for name fields
        and supports partial matching using LIKE operations.

        Args:
            page (int): The 1-based page number for pagination. Must be greater than 0.
                Used to calculate the offset for database query results.
            size (int): The number of records to return per page. Must be greater than 0.
                Determines the LIMIT clause in the SQL query.
            search_query (str): The search term to look for across student fields.
                Can be empty/None to return all students. For DNI searches, performs
                exact matching. For name searches, performs case-insensitive partial
                matching using SQL LIKE with wildcards.

        Returns:
            Page: A paginated response with the same structure as get_pageable_students:
                - data (List[Dict]): List of matching student records with all fields
                    including joined grade_name and section_name.
                - meta (Pagination): Pagination information including total count of
                    matching records, current page, total pages, and navigation links.

        Raises:
            ValueError: If page or size parameters are invalid (≤ 0).
            SQLAlchemyError: If database query execution fails.
            TransactionError: If the database transaction encounters an error.

        Note:
            The search logic uses OR conditions to match any of the following:
            - Exact DNI match (Student.dni == search_query)
            - Partial match in names (case-insensitive, contains search_query)
            - Partial match in paternal surname (case-insensitive, contains search_query)
            - Partial match in maternal surname (case-insensitive, contains search_query)

            When search_query is empty or None, the method efficiently returns all
            students without applying WHERE conditions, improving performance for
            "show all" scenarios.
        """
        offset_value = (page - 1) * size

        if not search_query:
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
                .offset(offset_value)
                .limit(size)
            )
        else:
            normalized_search = search_query.lower()

            conditions = [
                Student.dni == search_query,
                func.lower(Student.names).like(f"%{normalized_search}%"),
                func.lower(Student.paternal_surname).like(f"%{normalized_search}%"),
                func.lower(Student.maternal_surname).like(f"%{normalized_search}%"),
            ]

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
                .where(or_(*conditions))
                .offset(offset_value)
                .limit(size)
            )

        result = await self.session.exec(stmt)
        students_data = [dict(row._mapping) for row in result]

        if not search_query:
            count_stmt = select(func.count(Student.id))
        else:
            count_stmt = select(func.count(Student.id)).where(or_(*conditions))

        count_result = await self.session.exec(count_stmt)
        total_items = count_result.first()

        total_pages = math.ceil(total_items / size) if total_items > 0 else 1
        next_page = page + 1 if page < total_pages else None
        previous_page = page - 1 if page > 1 else None

        return Page(
            data=students_data,
            meta=Pagination(
                current_page=page,
                per_page=size,
                total=total_items,
                total_pages=total_pages,
                next_page=next_page,
                previous_page=previous_page,
            ),
        )
