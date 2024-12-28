from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.redis import init_redis, close_redis
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Kavas Capital Options API",
        description="Real-time options data and analytics",
        version="1.0.0",
        debug=settings.DEBUG
    )

    # CORS middleware configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600,  # Maximum time to cache preflight requests (10 minutes)
    )

    # Add routes
    app.include_router(api_router, prefix="/api/v1")

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.debug(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.debug(f"Response status: {response.status_code}")
        return response

    @app.on_event("startup")
    async def startup_event():
        """Initialize connections on startup"""
        logger.info("Starting up application...")
        try:
            # Initialize Redis
            await init_redis()
            logger.info("Redis initialized successfully")
        except Exception as e:
            logger.error(f"Error during startup: {str(e)}")
            raise

    @app.on_event("shutdown")
    async def shutdown_event():
        """Clean up connections on shutdown"""
        logger.info("Shutting down application...")
        try:
            # Close Redis connection
            await close_redis()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )
