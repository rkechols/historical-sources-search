import logging
from contextlib import asynccontextmanager
from typing import Annotated, cast

import httpx
from fastapi import Depends, FastAPI, Request
from playwright.async_api import Browser, Playwright, async_playwright
from pydantic import BaseModel

from historical_sources_search.env import Env
from historical_sources_search.search import search_all
from historical_sources_search.search_result import SearchResult

LOGGER = logging.getLogger(__name__)


@asynccontextmanager
async def _lifespan(api_: FastAPI):
    env = Env.get()
    async with (
        httpx.AsyncClient(follow_redirects=True) as httpx_client,
        async_playwright() as pw,
        await cast(Playwright, pw).chromium.launch(channel="chromium", headless=(not env.playwright_debug)) as browser,
    ):
        api_.state.httpx_client = httpx_client
        api_.state.browser = browser
        yield


async def _httpx_client_dep(request: Request) -> httpx.AsyncClient:
    return request.app.state.httpx_client


HttpxClientDep = Annotated[httpx.AsyncClient, Depends(_httpx_client_dep)]


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
async def post_search(request: SearchRequest, httpx_client: HttpxClientDep, browser: BrowserDep) -> SearchResponse:
    LOGGER.info(f"Starting search with query {request.query!r}")
    results = [result async for result in search_all(request.query, httpx_client, browser)]
    # TODO: stream results
    LOGGER.info(f"Found {len(results)} result(s) for query {request.query!r}")
    return SearchResponse(query=request.query, results=results)
