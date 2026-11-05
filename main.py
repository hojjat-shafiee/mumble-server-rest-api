import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.ice_manager import ice_manager
from app.server_router import router as server_router
from app.models import HealthResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("mumble_rest")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and teardown lifecycle.
    Gracefully initializes and destroys the ZeroC Ice communicator.
    """
    logger.info("Initializing Mumble REST API application...")
    try:
        if ice_manager.is_available():
            ice_manager.connect()
        else:
            logger.warning(
                "ZeroC Ice bindings are not available in this environment. "
                "Running in decoupled/mock mode."
            )
    except Exception as e:
        logger.warning(
            "Could not connect to Murmur on startup (%s). "
            "Endpoints requiring Ice will attempt connection on demand.", e
        )
    yield
    logger.info("Shutting down Mumble REST API application...")
    ice_manager.close()


mumble_rest: FastAPI = FastAPI(
    title="Mumble Server REST API",
    description="Modern RESTful API to manage and administer virtual Mumble (Murmur) voice servers via ZeroC Ice RPC.",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount routes under both /servers (standard REST) and /server (legacy compatibility)
mumble_rest.include_router(server_router, prefix="/servers")
mumble_rest.include_router(server_router, prefix="/server", include_in_schema=False)


@mumble_rest.get("/", summary="Root status and API version")
def root():
    """Returns the service name and API version."""
    return {
        "service": "mumble-server-rest-api",
        "version": mumble_rest.version,
        "docs_url": "/docs",
    }


@mumble_rest.get(
    "/healthz",
    response_model=HealthResponse,
    summary="Liveness and readiness health check",
    tags=["Health"],
)
@mumble_rest.get("/health", response_model=HealthResponse, include_in_schema=False)
def health_check():
    """
    Probes Murmur Ice connection health and returns service status.
    """
    return ice_manager.check_health()
