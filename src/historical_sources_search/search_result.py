from pydantic import BaseModel


class CollectionInfo(BaseModel):
    name: str
    url: str


class SearchResult(BaseModel):
    url: str
    title: str
    detail: str | None
    image_src: str | None
    provided_by_collection: CollectionInfo
