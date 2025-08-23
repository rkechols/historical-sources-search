import type SearchResult from "../models/search-result.ts"

interface SearchResultCardProps {
  searchResult: SearchResult
}

export default function SearchResultCard({ searchResult }: SearchResultCardProps) {
  return (
    <a className="result-card-link" href={searchResult.url} target="_blank" rel="noopener noreferrer">
      <div className="result-card">
        <div className="result-card-title">{searchResult.title || searchResult.url}</div>
        <div className="result-card-detail">
          {!!searchResult.image_src && (
            <img src={searchResult.image_src} alt={searchResult.title || "no caption"} />
          )}
          {!!searchResult.detail && (
            <p>{searchResult.detail}</p>
          )}
        </div>
        <p className="result-card-source">
          Source Collection: <a href={searchResult.provided_by_collection.url} target="_blank" rel="noopener noreferrer">
            {searchResult.provided_by_collection.name}
          </a>
        </p>
      </div>
    </a>
  )
}
