import type SearchResult from "../models/search-result"
import SearchResultCard from "./SearchResultCard"

export class SearchStateI {
  query: string
  constructor(query: string) {
    this.query = query
  }
}

export class SearchStatePending extends SearchStateI {}

export class SearchStateSuccess extends SearchStateI {
  results: SearchResult[]
  constructor(query: string, results: SearchResult[]) {
    super(query)
    this.results = results
  }
}

export class SearchStateError extends SearchStateI {}

interface SearchResultsProps {
  searchState: SearchStateI | null
}

function SearchResults({ searchState }: SearchResultsProps) {
  if (searchState == null) {
    return <p>Enter a search query to begin.</p>
  }
  if (searchState instanceof SearchStatePending) {
    // TODO: add a spinner
    return <p>Search pending: {searchState.query}</p>
  }
  if (searchState instanceof SearchStateSuccess) {
    const { query, results } = searchState
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
  if (searchState instanceof SearchStateError) {
    return <p>Unexpected error when searching for: {searchState.query}</p>
  }
  console.error("Unexpected searchState value:", searchState)
  return <p>Unexpected Error</p>
}

export default SearchResults
