import type CollectionInfo from "./collection-info.ts"

export default interface SearchResult {
  url: string
  title: string
  detail?: string | null
  image_src?: string | null
  provided_by_collection: CollectionInfo
}
