import logging
from collections.abc import AsyncIterable

import httpx
from playwright.async_api import Browser

from historical_sources_search.collections.base import CollectionBase
from historical_sources_search.collections.facing_history import CollectionFacingHistory
from historical_sources_search.collections.library_of_congress import CollectionLibraryOfCongress
from historical_sources_search.search_result import SearchResult

LOGGER = logging.getLogger(__name__)


async def search_all(query: str, httpx_client: httpx.AsyncClient, browser: Browser) -> AsyncIterable[SearchResult]:
    LOGGER.debug(f"{httpx_client = }")

    collections: list[CollectionBase] = [
        CollectionFacingHistory(browser),
        CollectionLibraryOfCongress(browser),
        # TODO: add more collections
    ]

    # TODO: use a queue and workers
    for collection in collections:
        async for result in collection.search(query):
            yield result
