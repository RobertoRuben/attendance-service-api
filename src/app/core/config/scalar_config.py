from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from scalar_fastapi import Layout, SearchHotKey


def get_scalar_docs(app: FastAPI, prefix: str = "/api/v1"):
    """
    Get the Scalar API documentation configuration.

    This function creates a Scalar API documentation interface with customized settings
    for better developer experience. It provides an interactive API documentation
    with modern layout, dark mode, and multiple server configurations.

    Args:
        app (FastAPI): The FastAPI application instance containing the OpenAPI specification.
        prefix (str, optional): The API prefix path used for routing. Defaults to "/api/v1".
    """
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
        layout=Layout.MODERN,
        show_sidebar=True,
        hide_download_button=True,
        hide_models=False,
        hide_client_button=False,
        dark_mode=True,
        search_hot_key=SearchHotKey.K,
        default_open_all_tags=False,
        servers=[
            {"url": "http://localhost:8000", "description": "Development server"},
            {"url": "https://api.tudominio.com", "description": "Production server"},
        ],
    )


def configure_scalar_route(app: FastAPI, prefix: str = "/api/v1"):
    """
    Configure and register the Scalar documentation route in the FastAPI application.

    This function creates a GET endpoint that serves the Scalar API documentation
    interface. The route is excluded from the OpenAPI schema to avoid circular
    references and provides a clean documentation experience.

    Args:
        app (FastAPI): The FastAPI application instance where the documentation
                      route will be registered.
        prefix (str, optional): The API prefix path for the documentation endpoint.
                               Defaults to "/api/v1". The final route will be
                               "{prefix}/scalar".

    Returns:
        None: This function modifies the FastAPI app instance in-place by adding
              the documentation route.
    """

    @app.get(f"{prefix}/scalar", include_in_schema=False, name="scalar_docs")
    async def scalar_html():
        """
        Serve the Scalar API documentation HTML interface.

        Returns:
            HTMLResponse: The rendered Scalar documentation interface with all
                         configured settings and styling.
        """
        return get_scalar_docs(app, prefix)
