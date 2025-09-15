from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.app.core.db import init_db
from src.app.core.exception import register_exception_handlers
from src.app.domain.root.controller import root_router, root_tags_metadata
from src.app.domain.classrooms.controller import grade_router, grades_tags_metadata
from src.app.domain.classrooms.controller import section_router, sections_tags_metadata
from src.app.domain.students.controller import student_router, students_tags_metadata
from src.app.core.config.scalar_config import configure_scalar_route
from src.app.core.monitoring.controller import health_router, health_tags_metadata

API_PREFIX = "/api/v1"

tags_metadata = [
    grades_tags_metadata,
    sections_tags_metadata,
    health_tags_metadata,
    root_tags_metadata,
    students_tags_metadata,
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await register_exception_handlers(app)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Attendance Service API",
        description="API for managing attendance",
        version="1.0.0",
        openapi_tags=tags_metadata,
        debug=True,
        lifespan=lifespan,
        docs_url=f"{API_PREFIX}/docs",
        redoc_url=f"{API_PREFIX}/redoc",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": 1,
            "deepLinking": True,
            "displayRequestDuration": True,
            "filter": True,
            "showExtensions": True,
            "syntaxHighlight.theme": "arta",
            "theme": "dark",
            "tryItOutEnabled": True,
        },
    )

    configure_scalar_route(app, API_PREFIX)

    app.include_router(root_router)
    app.include_router(health_router, prefix=API_PREFIX)
    app.include_router(grade_router, prefix=API_PREFIX)
    app.include_router(section_router, prefix=API_PREFIX)
    app.include_router(student_router, prefix=API_PREFIX)

    return app


app = create_app()
