import type SearchResult from "../models/search-result"

export class APIError extends Error {
  constructor(message: string) {
    super(message)
    this.name = "APIError"
  }
}

export interface SearchResponse {
    query: string
    results: SearchResult[]
}

class API {
  async postSearch(query: string): Promise<SearchResponse> {
    const response = await fetch("/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    })
    if (!response.ok) {
      throw new APIError(`API request "POST /search" failed with status ${response.status.toString()}`)
    }
    return (await response.json()) as SearchResponse
  }
}

const api = new API()

export default api
