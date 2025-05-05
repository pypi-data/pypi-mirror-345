import logging

from fastapi import FastAPI

from src.epona.auth import routers as auth
from src.epona.pessoas import routers as pessoas

from .routes import ping

log = logging.getLogger("uvicorn")


def create_application() -> FastAPI:
    application = FastAPI(name="api-core")

    application.include_router(auth.router, prefix="/auth", tags=["auth"])
    application.include_router(pessoas.router, prefix="/pessoas", tags=["pessoas"])
    application.include_router(ping.router, prefix="/ping", tags=["ping"])

    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
