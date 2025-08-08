import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

LOGGER = logging.getLogger(__name__)


@asynccontextmanager
async def _lifespan(api_: FastAPI):
    LOGGER.info(f"lifespan start ({api_})")
    yield
    LOGGER.info(f"lifespan end ({api_})")


api = FastAPI(lifespan=_lifespan)


@api.get("/")
async def get_root() -> dict[str, str]:
    return {"status": "ok"}
