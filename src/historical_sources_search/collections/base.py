from abc import ABC, abstractmethod
from collections.abc import AsyncIterable

from historical_sources_search.search_result import CollectionInfo, SearchResult


class CollectionBase(ABC):
    def __init__(self, collection_info: CollectionInfo):
        super().__init__()
        self.collection_info = collection_info

    @abstractmethod
    def search(self, query: str) -> AsyncIterable[SearchResult]:
        raise NotImplementedError("Must be implemented by child class")
