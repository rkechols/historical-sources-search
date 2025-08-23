import type SearchResult from "../models/search-result.ts"

interface SearchResultCardProps {
  searchResult: SearchResult
}

export default function SearchResultCard({ searchResult }: SearchResultCardProps) {
  return (
    <a className="result-card-link" href={searchResult.url} target="_blank" rel="noopener noreferrer">
      <div className="result-card">
        <div>
          <div className="result-card-title">{searchResult.title || searchResult.url}</div>
          <div className="result-card-content">
            {!!searchResult.image_src && (
              <img src={searchResult.image_src} alt={searchResult.title || "no caption"} />
            )}
            {!!searchResult.detail && (
              <div className="result-card-detail">{searchResult.detail}</div>
            )}
          </div>
        </div>
      </div>
    </a>
  )
}
