from functools import lru_cache
from typing import Self

from pydantic_settings import BaseSettings


class Env(BaseSettings):
    playwright_debug: bool = False

    @classmethod
    @lru_cache(maxsize=1)
    def get(cls) -> Self:
        return cls()
