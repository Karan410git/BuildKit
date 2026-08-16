from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.upload import router as upload_router
from app.core.config import settings
from app.core.logging import setup_logging


def get_application() -> FastAPI:
    """Create and configure the FastAPI application.

    Logging is configured during initialization so that every module
    using ``logging.getLogger(__name__)`` inherits the centralized
    configuration from ``settings.log_level``.
    """
    setup_logging()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )

    app.include_router(health_router)
    app.include_router(upload_router)

    return app


app = get_application()
