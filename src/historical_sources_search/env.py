from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic_settings import BaseSettings

MEDIA_DIR = Path("media")
PLAYWRIGHT_TRACES_DIR = MEDIA_DIR / "traces"


class Env(BaseSettings):
    playwright_debug: bool = False
    api_port: int = 8000

    @classmethod
    @lru_cache(maxsize=1)
    def get(cls) -> Self:
        return cls()
