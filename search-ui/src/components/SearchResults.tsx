import type SearchResult from "../models/search-results.ts"
import SearchResultCard from "./SearchResultCard.tsx"

interface SearchResultsProps {
  query: string
  results: SearchResult[]
}

export default function SearchResults({ query, results }: SearchResultsProps) {
  if (results.length === 0) {
    return <p>No results found for: {query}</p>
  }
  return <div>
    <h2>Search Results for: {query}</h2>
    { results.map(result => (
      <SearchResultCard key={result.url} searchResult={result} />
    ))}
  </div>
}
