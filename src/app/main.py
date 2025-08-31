from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.app.core.db import init_db
from src.app.core.exception import register_exception_handlers
from src.app.domain.classrooms.controller import grade_router, grades_tags_metadata

API_PREFIX = "/api/v1"

tags_metadata = [grades_tags_metadata]


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await register_exception_handlers(app)
    yield


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

app.include_router(grade_router, prefix=API_PREFIX)
