import logging

from fastapi import FastAPI
from tortoise import Tortoise

from src.app.db import models
from src.epona.auth import routers as auth
from src.epona.pessoas import routers as pessoas
from src.epona.layers import routers as layers

from .routes import ping

log = logging.getLogger("uvicorn")


def create_application() -> FastAPI:
    application = FastAPI(name="api-core")

    application.include_router(auth.router, prefix="/auth", tags=["auth"])
    application.include_router(pessoas.router, prefix="/pessoas", tags=["pessoas"])
    application.include_router(ping.router, prefix="/ping", tags=["ping"])
    application.include_router(layers.router, prefix="/layers", tags=["layers"])

    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    Tortoise.init_models(models, "models")


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
