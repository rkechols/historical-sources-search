import logging
from collections.abc import AsyncIterable
from typing import override
from urllib.parse import urlencode, urljoin

from playwright.async_api import Browser, TimeoutError as PlaywrightTimeoutError, expect as pw_expect

from historical_sources_search.collections.base import CollectionBase
from historical_sources_search.exceptions import NavigationError
from historical_sources_search.search_result import CollectionInfo, SearchResult

LOGGER = logging.getLogger(__name__)


class CollectionLibraryOfCongress(CollectionBase):
    def __init__(self, browser: Browser):
        super().__init__(
            collection_info=CollectionInfo(
                name="Classroom Materials at the Library of Congress",
                url="https://www.loc.gov/classroom-materials/?fa=partof_type%3Aprimary+source+set",
            ),
        )
        self.browser = browser

    @override
    async def search(self, query: str) -> AsyncIterable[SearchResult]:
        async with (
            await self.browser.new_context() as browser_context,
            await browser_context.new_page() as page,
        ):
            url_params = urlencode(
                {
                    "q": query,
                    "fa": "partof_type:primary source set",
                    "st": "list",
                    "c": "150",  # results per page
                }
            )
            search_url = f"https://www.loc.gov/classroom-materials/?{url_params}"
            response = await page.goto(search_url)
            if response is not None and not response.ok:
                raise NavigationError(f"Navigation to `{search_url}` failed with status {response.status}")

            try:
                await pw_expect(page.locator(".noresults-for")).to_be_visible(timeout=5_000)
            except AssertionError:  # does *not* have a "no results" message
                pass
            else:  # *does* have a "no results" message
                LOGGER.info(f"No results found for query {query!r}")
                return

            page_number = 1
            while True:  # turn through all pages
                LOGGER.debug(f"Page number {page_number} of query {query!r}")

                results_list = page.locator("[id=results]")
                await pw_expect(results_list).to_be_visible(timeout=10_000)
                page_url = page.url

                i = 0
                while True:  # get all results from this page
                    item = results_list.locator("li.item").nth(i)
                    try:
                        await pw_expect(item).to_be_visible(timeout=(10_000 if i == 0 else 500))
                    except AssertionError:
                        break  # no more results on this page

                    item_title = item.locator(".item-description-title").locator("a")
                    item_title_href = await item_title.get_attribute("href")
                    if not item_title_href:
                        item_title_html = await item_title.inner_html()
                        LOGGER.warning(f"Search result did not have an href: {item_title_html}")
                        continue
                    item_title_href = urljoin(page_url, item_title_href)
                    item_title_str = (await item_title.inner_text()).strip()
                    item_description = (await item.locator(".item-description-abstract").inner_text()).strip()

                    item_image = item.locator("figure").locator("img")
                    try:
                        item_image_src = await item_image.get_attribute("src", timeout=500)
                    except PlaywrightTimeoutError:
                        item_image_src = None
                    else:
                        if item_image_src:
                            item_image_src = urljoin(page_url, item_image_src)

                    yield SearchResult(
                        url=item_title_href,
                        title=item_title_str,
                        detail=item_description,
                        image_src=item_image_src,
                        provided_by_collection=self.collection_info,
                    )
                    i += 1

                # advance the page, if possible
                next_page_button = page.get_by_role("link", name="Next Page")
                try:
                    await pw_expect(next_page_button).to_be_visible(timeout=1_000)
                except AssertionError:
                    break  # no more pages
                await next_page_button.click()
                page_number += 1
