import { useState, useRef } from "react"
import "./App.css"
import { FaGithub } from "react-icons/fa"
import api from "./services/api.ts"
import type { SearchStateError, SearchStateI, SearchStatePending, SearchStateSuccess } from "./components/SearchState.tsx"
import SearchState from "./components/SearchState.tsx"

function App() {
  const queryInputRef = useRef<HTMLInputElement | null>(null)
  const [searchState, setSearchState] = useState<SearchStateI | null>(null)

  const searchInProgress = searchState?.type === "pending"

  function submitQuery() {
    const queryInput = queryInputRef.current
    if (!queryInput) {
      console.error("queryInput not found")
      return
    }
    const query = queryInput.value

    console.log(`Submitting query: ${query}`)
    setSearchState({ type: "pending", query } as SearchStatePending)
    api.postSearch(query).then(newSearchResponse => {
      setSearchState({ type: "success", query, results: newSearchResponse.results } as SearchStateSuccess)
    }).catch((error: unknown) => {
      if (error instanceof Error) {
        console.error(`Error occurred while executing search: ${error.message}`)
      } else {
        console.error("Non-Error object caught:", error)
      }
      setSearchState({ type: "error", query } as SearchStateError)
    })
  }

  return (
    <>
      <h1>Historical Sources Search</h1>
      <a href="https://github.com/rkechols/historical-sources-search" target="_blank" rel="noopener noreferrer">
        Source Code on GitHub
        <span aria-hidden="true">
          <FaGithub />
        </span>
      </a>
      <div className="card">
        <input id="search-query" aria-label="search-query" type="text" placeholder="Type your search query here" ref={queryInputRef} />
        <button id="search-query-submit" aria-label="search-query-submit" type="button" onClick={submitQuery} disabled={searchInProgress}>
          Search
        </button>
      </div>
      <SearchState searchState={searchState} />
    </>
  )
}

export default App
