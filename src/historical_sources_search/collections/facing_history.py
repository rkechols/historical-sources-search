from collections.abc import AsyncIterable
from typing import override

import httpx
from playwright.async_api import Browser

from historical_sources_search.collections.base import CollectionBase
from historical_sources_search.search_result import CollectionInfo, SearchResult


class CollectionFacingHistory(CollectionBase):
    def __init__(self, httpx_client: httpx.AsyncClient, browser: Browser):
        super().__init__(
            collection_info=CollectionInfo(
                name="Facing History",
                url="https://www.facinghistory.org/resource-library",
            ),
        )
        self.httpx_client = httpx_client
        self.browser = browser

    @override
    async def search(self, query: str) -> AsyncIterable[SearchResult]:
        # TODO: get real results
        example_result = SearchResult(
            title="example title",
            url="example result URL",
            detail="example detail",
            provided_by_collection=self.collection_info,
        )
        yield example_result
