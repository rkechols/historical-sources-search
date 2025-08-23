import type SearchResult from "../models/search-results.ts"

interface SearchResultCardProps {
  searchResult: SearchResult
}

export default function SearchResultCard({ searchResult }: SearchResultCardProps) {
  return <a href={searchResult.url} target="_blank" rel="noopener noreferrer">
    <div>
      {!!searchResult.image_src && (<img src={searchResult.image_src} alt={searchResult.title || "no caption"} />)}
      <div>
        {searchResult.title || searchResult.url}
        {!!searchResult.detail && (<p>{searchResult.detail}</p>)}
      </div>
    </div>
  </a>
}
