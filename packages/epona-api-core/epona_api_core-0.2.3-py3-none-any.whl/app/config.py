import logging
import os
from functools import lru_cache

from pydantic import AnyUrl, BaseSettings

log = logging.getLogger("uvicorn")


_db_host = os.getenv("DB_HOST", "localhost")
_db_user = os.getenv("DB_USER", "postgres")
_db_name = os.getenv("DB_NAME", "core")
_db_password = os.getenv("DB_PASSWORD", "postgres")


class Settings(BaseSettings):
    aws_region: str = os.getenv("AWS_DEFAULT_REGION")
    database_url: AnyUrl = (
        f"postgres://{_db_user}:{_db_password}@{_db_host}:5432/{_db_name}"
    )
    environment: str = "dev"
    host: str = os.getenv("HOST_URL")
    limit: int = os.getenv("LIMIT", 200)
    testing: bool = 0


@lru_cache()
def get_settings() -> Settings:
    log.info("Loading configuration from environment")
    return Settings()
