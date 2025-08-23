import { useState, useRef } from "react"
import "./App.css"
import { FaGithub } from "react-icons/fa"
import api from "./services/api.ts"
import type { SearchStateI} from "./components/SearchResults.tsx"
import { SearchStateError, SearchStatePending, SearchStateSuccess } from "./components/SearchResults.tsx"
import SearchResults from "./components/SearchResults.tsx"

function App() {
  const queryInputRef = useRef<HTMLInputElement | null>(null)
  const [searchState, setSearchState] = useState<SearchStateI | null>(null)

  const searchInProgress = searchState instanceof SearchStatePending

  function submitQuery() {
    const queryInput = queryInputRef.current
    if (!queryInput) {
      console.error("queryInput not found")
      return
    }
    const query = queryInput.value

    console.log(`Submitting query: ${query}`)
    setSearchState(new SearchStatePending(query))
    api.postSearch(query).then(newSearchResponse => {
    setSearchState(new SearchStateSuccess(query, newSearchResponse.results))
    }).catch((error: unknown) => {
      if (error instanceof Error) {
        console.error(`Error occurred while executing search: ${error.message}`)
      } else {
        console.error("Non-Error object caught:", error)
      }
      setSearchState(new SearchStateError(query))
    })
  }

  return (
      <div className="app-container">
        <h1 className="app-title">Historical Sources Search</h1>
        <a className="github-link" href="https://github.com/rkechols/historical-sources-search" target="_blank" rel="noopener noreferrer">
          Source Code on GitHub
          <span aria-hidden="true">
            <FaGithub />
          </span>
        </a>
        <div className="search-bar">
          <input id="search-query" aria-label="search-query" type="text" placeholder="Type your search query here" ref={queryInputRef} />
          <button id="search-query-submit" aria-label="search-query-submit" type="button" onClick={submitQuery} disabled={searchInProgress}>
            Search
          </button>
        </div>
        <div className="results-container">
          <SearchResults searchState={searchState} />
        </div>
      </div>
  )
}

export default App
