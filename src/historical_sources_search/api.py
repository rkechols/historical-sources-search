import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from historical_sources_search.search import Search
from historical_sources_search.search_result import SearchResult

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


class SearchRequest(BaseModel):
    query: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


@api.post("/search")
async def post_search(request: SearchRequest) -> SearchResponse:
    search = Search(request.query)
    await search.execute()
    return SearchResponse(query=search.query, results=search.results)
