import time

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.api.v1.routers import api_router
from src.core.config import settings
from src.core.error_handlers import setup_exception_handlers

# Metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency")

# Structured logging
logger = structlog.get_logger()
limiter = Limiter(key_func=get_remote_address)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.API_VERSION,
        description="""
        Hello World API - A production-ready FastAPI application.
        Features:
        - Authentication & Authorization
        - Rate Limiting
        - Metrics & Monitoring
        - Structured Logging
        - Database Integration
        - Error Handling
        """,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup security, error handlers, and routers
    setup_exception_handlers(app)
    app.include_router(api_router)

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        # Record metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).inc()
        REQUEST_LATENCY.observe(time.time() - start_time)
        return response

    @app.get("/health")
    async def health_check():
        return JSONResponse({"status": "healthy"})

    return app


app = create_app()


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{settings.PROJECT_NAME} - API Documentation",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


if __name__ == "__main__":
    import uvicorn

    # Use localhost by default, override with environment variable if needed
    host = settings.HOST if hasattr(settings, "HOST") else "127.0.0.1"
    port = settings.PORT if hasattr(settings, "PORT") else 8000

    uvicorn.run(app, host=host, port=port)
