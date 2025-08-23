import type SearchResult from "../models/search-results"
import SearchResults from "./SearchResults"

export interface SearchStateI {
  type: "pending" | "success" | "error"
  query: string
}

export interface SearchStatePending extends SearchStateI {
  type: "pending"
}

export interface SearchStateSuccess extends SearchStateI {
  type: "success"
  results: SearchResult[]
}

export interface SearchStateError extends SearchStateI {
  type: "error"
}

interface SearchStateProps {
  searchState: SearchStateI | null
}

export default function SearchState({ searchState }: SearchStateProps) {
  if (searchState == null) {
    return <p>Enter a search query to begin.</p>
  }
  if (searchState.type === "pending") {
    const searchPending = searchState as SearchStatePending
    // TODO: add a spinner
    return <p>Search pending: {searchPending.query}</p>
  } else if (searchState.type === "success") {
    const searchSuccess = searchState as SearchStateSuccess
    return <SearchResults query={searchSuccess.query} results={searchSuccess.results} />
  } else {  // searchState.type === "error"
    const searchError = searchState as SearchStateError
    return <p>Unexpected error when searching for: {searchError.query}</p>
  }
}
