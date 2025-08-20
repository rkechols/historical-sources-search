import { useState, useRef } from "react"
import "./App.css"
import { FaGithub } from "react-icons/fa"
import SearchResults from "./components/SearchResults.tsx"
import type SearchResult from "./models/search-results.ts"

function App() {
  const queryInputRef = useRef<HTMLInputElement | null>(null)
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])

  function submitQuery() {
    const queryInput = queryInputRef.current
    if (!queryInput) {
      console.error("queryInput not found")
      return
    }
    const query = queryInput.value

    // TODO
    console.log(`TODO - submit query: ${query}`)
    setSearchResults((results) => [...results, {
      url: `https://github.com/rkechols/historical-sources-search?ignore=${results.length.toString()}`,
      title: query,
      provided_by_collection: {
        name: "Fake",
        url: "https://www.fake.com",
      },
    }])
  }

  return (
    <>
      <h1>Historical Sources Search</h1>
      <a href="https://github.com/rkechols/historical-sources-search" target="_blank" rel="noopener noreferrer">
        Source Code on GitHub
        <FaGithub alt="GitHub logo" />
      </a>
      <div className="card">
        <input id="search-query" aria-label="search-query" type="text" placeholder="Type your search query here" ref={queryInputRef} />
        <button id="search-query-submit" aria-label="search-query-submit" type="button" onClick={submitQuery}>
          Search
        </button>
      </div>
      <SearchResults results={searchResults} />
    </>
  )
}

export default App
