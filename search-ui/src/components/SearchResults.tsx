import type SearchResult from "../models/search-results.ts"
import SearchResultCard from "./SearchResultCard.tsx"

interface SearchResultsProps {
  results: SearchResult[]
}

export default function SearchResults({ results }: SearchResultsProps) {
  return <div>
    { results.map(result => (
      <SearchResultCard key={result.url} searchResult={result} />
    ))}
  </div>
}
