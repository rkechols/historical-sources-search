from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from historical_sources_search.search_result import SearchResult


class SourceCollectionBase(ABC):
    def __init__(self, info_url: str):
        super().__init__()
        self.info_url = info_url

    @abstractmethod
    def search(self, query: str) -> AsyncIterator[SearchResult]:
        raise NotImplementedError("Must be implemented by child class")
