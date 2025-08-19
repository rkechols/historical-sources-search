import re
from typing import override
from urllib.parse import urlencode

from playwright.async_api import Browser, Locator, Page, TimeoutError as PlaywrightTimeoutError, expect as pw_expect

from historical_sources_search.collections.base_browser_paging import CollectionBaseBrowserPaging
from historical_sources_search.exceptions import MissingInformationError, NavigationError
from historical_sources_search.search_result import CollectionInfo


class CollectionFacingHistory(CollectionBaseBrowserPaging):
    """
    https://www.facinghistory.org/robots.txt includes the following restriction:

        # NOTICE: The collection of content and other data on this
        # site through automated means, including any device, tool,
        # or process designed to data mine or scrape content, is
        # prohibited except (1) for the purpose of search engine indexing or
        # artificial intelligence retrieval augmented generation or (2) with express
        # written permission from this site’s operator.

    I assert that [this project](https://github.com/rkechols/historical-sources-search/)
    falls within the bounds of exception (1).
    """  # noqa: RUF002

    def __init__(self, browser: Browser):
        super().__init__(
            browser=browser,
            collection_info=CollectionInfo(
                name="Facing History",
                url="https://www.facinghistory.org/resource-library",
            ),
        )

    @override
    async def _enter_query(self, page: Page, query: str):
        url_params = urlencode(
            {
                "keys": query,
                "sort_by": "search_api_relevance",
                "items_per_page": "48",
            }
        )
        search_url = f"https://www.facinghistory.org/resource-library?{url_params}"
        response = await page.goto(search_url)
        if response is not None and not response.ok:
            raise NavigationError(f"Navigation to `{search_url}` failed with status {response.status}")
        await page.get_by_role("button", name="Close").click()

    @override
    def _get_locator_no_results(self, page: Page) -> Locator:
        return page.locator(".search-no-results-message")

    @override
    def _get_locator_result_by_index(self, page: Page, index: int) -> Locator:
        return page.locator(".card-list").locator(".card").nth(index)

    @override
    async def _get_result_url(self, page: Page, result_locator: Locator) -> str:
        card_link = result_locator.locator("a.card__link")
        card_link_href = await card_link.get_attribute("href")
        if not card_link_href:
            card_link_html = await card_link.inner_html()
            raise MissingInformationError(f"Search result did not have an href: {card_link_html}")
        return card_link_href

    @override
    async def _get_result_title(self, page: Page, result_locator: Locator) -> str:
        return await result_locator.locator(".card__header").inner_text(timeout=500)

    @override
    async def _get_result_detail(self, page: Page, result_locator: Locator) -> str | None:
        return await result_locator.locator(".card__summary").inner_text(timeout=500)

    @override
    async def _get_result_image_src(self, page: Page, result_locator: Locator) -> str | None:
        card_image = result_locator.locator(".card__image").locator("img")
        try:
            return await card_image.get_attribute("src", timeout=500)
        except PlaywrightTimeoutError:
            return None

    @override
    async def _advance_page(self, page: Page, current_page_index: int) -> bool:
        current_page_number = current_page_index + 1
        next_page_button = page.locator("li.pager__item--next")
        try:
            await pw_expect(next_page_button).to_be_visible(timeout=1_000)
        except AssertionError:
            return False  # no more pages
        await next_page_button.click()
        # make sure the new page is loaded
        new_page_number = current_page_number + 1
        await pw_expect(page.locator(".pager__link.is-active")).to_have_text(
            re.compile(f"\\b{new_page_number}\\b"),
            use_inner_text=True,
            timeout=30_000,
        )
        return True
