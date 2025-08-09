from pydantic import BaseModel


class CollectionInfo(BaseModel):
    name: str
    url: str


class SearchResult(BaseModel):
    title: str
    url: str
    detail: str | None
    provided_by_collection: CollectionInfo
