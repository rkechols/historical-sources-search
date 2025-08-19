import logging
from collections.abc import AsyncIterable
from typing import override
from urllib.parse import quote as url_escape, urljoin

from playwright.async_api import Browser, expect as pw_expect

from historical_sources_search.collections.base import CollectionBase
from historical_sources_search.exceptions import NavigationError
from historical_sources_search.search_result import CollectionInfo, SearchResult

LOGGER = logging.getLogger(__name__)


class CollectionConstitutionAnnotated(CollectionBase):
    def __init__(self, browser: Browser):
        super().__init__(
            collection_info=CollectionInfo(
                name="Constitution Annotated",
                url="https://constitution.congress.gov/",
            ),
        )
        self.browser = browser

    @override
    async def search(self, query: str) -> AsyncIterable[SearchResult]:
        async with (
            await self.browser.new_context() as browser_context,
            await browser_context.new_page() as page,
        ):
            query_escaped = url_escape(query, safe="")
            search_url = f"https://constitution.congress.gov/search/{query_escaped}"
            response = await page.goto(search_url)
            if response is not None and not response.ok:
                raise NavigationError(f"Navigation to `{search_url}` failed with status {response.status}")

            try:  # TODO
                await pw_expect(page.get_by_title("no-results")).to_be_visible(timeout=5_000)
            except AssertionError:  # does *not* have a "no results" message
                pass
            else:  # *does* have a "no results" message
                LOGGER.info(f"No results found for query {query!r}")
                return

            page_number = 1
            while True:  # turn through all pages
                LOGGER.debug(f"Page number {page_number} of query {query!r}")

                results_list = page.locator("ul.search-results")
                await pw_expect(results_list).to_be_visible(timeout=10_000)
                page_url = page.url

                i = 0
                while True:  # get all results from this page
                    item = page.locator("ul.search-results > li").nth(i)
                    try:
                        await pw_expect(item).to_be_visible(timeout=(10_000 if i == 0 else 500))
                    except AssertionError:
                        break  # no more results on this page

                    item_title = item.locator(".search-results-title")
                    item_title_link = item_title.locator("a")
                    item_title_href = await item_title_link.get_attribute("href")
                    if not item_title_href:
                        item_title_link_html = await item_title_link.inner_html()
                        LOGGER.warning(f"Search result did not have an href: {item_title_link_html}")
                        continue
                    item_title_href = urljoin(page_url, item_title_href)
                    item_title_str = (await item_title.inner_text()).strip()
                    item_description = (await item.locator(".search-results-summary").inner_text()).strip()

                    yield SearchResult(
                        url=item_title_href,
                        title=item_title_str,
                        detail=item_description,
                        image_src=None,
                        provided_by_collection=self.collection_info,
                    )
                    i += 1

                # advance the page, if possible
                next_page_button = page.locator(".search-results-control-pagination").get_by_role(
                    role="link",
                    name=str(page_number + 1),
                    exact=True,
                )
                try:
                    await pw_expect(next_page_button).to_be_visible(timeout=1_000)
                except AssertionError:
                    break  # no more pages
                await next_page_button.click()
                page_number += 1
