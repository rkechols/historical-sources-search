import logging

from playwright.async_api import Browser

from historical_sources_search.search_result import SearchResult
from historical_sources_search.source_collections.base import SourceCollectionBase
from historical_sources_search.source_collections.example_collection import ExampleCollection

LOGGER = logging.getLogger(__name__)

SOURCE_COLLECTIONS: list[SourceCollectionBase] = [
    ExampleCollection("https://example.com"),
]


class Search:
    def __init__(self, query: str, browser: Browser):
        super().__init__()
        self.query = query
        self.browser = browser
        self._results: list[SearchResult] = []

    @property
    def results(self) -> list[SearchResult]:
        return self._results

    async def execute(self):
        LOGGER.debug(f"{self.browser.browser_type.name = }")
        # TODO: use a queue and workers
        for source_collection in SOURCE_COLLECTIONS:
            async for result in source_collection.search(self.query):
                self._results.append(result)
