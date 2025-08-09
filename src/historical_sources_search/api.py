import logging
from contextlib import asynccontextmanager
from typing import Annotated, cast

from fastapi import Depends, FastAPI, Request
from playwright.async_api import Browser, Playwright, async_playwright
from pydantic import BaseModel

from historical_sources_search.env import Env
from historical_sources_search.search import Search
from historical_sources_search.search_result import SearchResult

LOGGER = logging.getLogger(__name__)


@asynccontextmanager
async def _lifespan(api_: FastAPI):
    LOGGER.info(f"lifespan start ({api_})")
    env = Env.get()
    async with (
        async_playwright() as pw,
        await cast(Playwright, pw).chromium.launch(channel="chromium", headless=(not env.playwright_debug)) as browser,
    ):
        api_.state.browser = browser
        yield
    LOGGER.info(f"lifespan end ({api_})")


async def _browser_dep(request: Request) -> Browser:
    return request.app.state.browser


BrowserDep = Annotated[Browser, Depends(_browser_dep)]


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
async def post_search(request: SearchRequest, browser: BrowserDep) -> SearchResponse:
    search = Search(request.query, browser)
    await search.execute()
    return SearchResponse(query=search.query, results=search.results)
