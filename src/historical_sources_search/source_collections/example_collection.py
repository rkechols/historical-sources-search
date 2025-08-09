from collections.abc import AsyncGenerator
from typing import override

from historical_sources_search.search_result import SearchResult
from historical_sources_search.source_collections.base import SourceCollectionBase


class ExampleCollection(SourceCollectionBase):
    @override
    async def search(self, query: str) -> AsyncGenerator[SearchResult]:
        yield SearchResult(title="example title", url="example result URL")  # TODO: take this out
