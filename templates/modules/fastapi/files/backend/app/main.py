from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.module_routes import register_module_routes


def get_application() -> FastAPI:
    setup_logging()
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    register_module_routes(app)
    return app


app = get_application()
