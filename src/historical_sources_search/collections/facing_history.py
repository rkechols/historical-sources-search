import logging
import random
import re
import string
import time
from collections.abc import AsyncIterable
from typing import override
from urllib.parse import urlencode, urljoin

import httpx
from playwright.async_api import Browser, TimeoutError as PlaywrightTimeoutError, expect as pw_expect

from historical_sources_search.collections.base import CollectionBase
from historical_sources_search.env import PLAYWRIGHT_TRACES_DIR, Env
from historical_sources_search.search_result import CollectionInfo, SearchResult

LOGGER = logging.getLogger(__name__)


class CollectionFacingHistory(CollectionBase):
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

    def __init__(self, httpx_client: httpx.AsyncClient, browser: Browser):
        super().__init__(
            collection_info=CollectionInfo(
                name="Facing History",
                url="https://www.facinghistory.org/resource-library",
            ),
        )
        self.httpx_client = httpx_client
        self.browser = browser

    @override
    async def search(self, query: str) -> AsyncIterable[SearchResult]:
        async with (
            await self.browser.new_context() as browser_context,
            await browser_context.new_page() as page,
        ):
            save_pw_trace = Env.get().playwright_debug
            if save_pw_trace:
                await browser_context.tracing.start(snapshots=True, screenshots=True, sources=True)
            try:
                url_params = urlencode(
                    {
                        "keys": query,
                        "sort_by": "search_api_relevance",
                        "items_per_page": "48",
                    }
                )
                search_url = f"https://www.facinghistory.org/resource-library?{url_params}"
                response = await page.goto(search_url)
                if response is not None:
                    LOGGER.debug(f"Navigation response status: {response.status}")

                await page.get_by_role("button", name="Close").click()
                # await page.locator("[data-test-id=\"interactive-frame\"]").content_frame.get_by_role("button", name="Close").click()
                # await page.get_by_role("button", name="Change view mode").click()

                page_number = 1
                while True:  # turn through all pages
                    LOGGER.debug(f"Page number: {page_number}")

                    # TODO: what if there are no results at all?

                    card_list = page.locator(".card-list")
                    await pw_expect(card_list).to_be_visible(timeout=10_000)
                    page_url = page.url

                    i = 0
                    while True:  # get all results from this page
                        card = card_list.locator(".card").nth(i)
                        try:
                            await pw_expect(card).to_be_visible(timeout=(10_000 if i == 0 else 500))
                        except AssertionError:
                            break  # no more results on this page
                        await card.scroll_into_view_if_needed()

                        card_link = card.locator("a.card__link")
                        card_link_href = await card_link.get_attribute("href")
                        if not card_link_href:
                            card_link_html = await card_link.inner_html()
                            LOGGER.warning(f"Search result did not have an href: {card_link_html}")
                            continue
                        card_link_href = urljoin(page_url, card_link_href)

                        card_header = (await card.locator(".card__header").inner_text()).strip()
                        card_summary = (await card.locator(".card__summary").inner_text()).strip()
                        card_image = card.locator(".card__image").locator("img")
                        try:
                            card_image_src = await card_image.get_attribute("src", timeout=500)
                        except PlaywrightTimeoutError:
                            card_image_src = None
                        else:
                            if card_image_src:
                                card_image_src = urljoin(page_url, card_image_src)

                        yield SearchResult(
                            url=card_link_href,
                            title=card_header,
                            detail=card_summary,
                            image_src=card_image_src,
                            provided_by_collection=self.collection_info,
                        )
                        i += 1

                    # advance the page, if possible
                    next_page_button = page.locator("li.pager__item--next")
                    try:
                        await pw_expect(next_page_button).to_be_visible(timeout=1_000)
                    except AssertionError:
                        break  # no more pages
                    await next_page_button.click()
                    page_number += 1
                    # make sure the new page is loaded
                    await pw_expect(page.locator(".pager__link.is-active")).to_have_text(
                        re.compile(f"\\b{page_number}\\b"),
                        use_inner_text=True,
                        timeout=30_000,
                    )

            finally:
                if save_pw_trace:
                    PLAYWRIGHT_TRACES_DIR.mkdir(parents=True, exist_ok=True)
                    timestamp = str(round(time.time()))
                    hex_ = "".join(random.choices(string.digits + "abcdef", k=8))
                    trace_filepath = PLAYWRIGHT_TRACES_DIR / f"trace-{timestamp}-{hex_}.zip"
                    await browser_context.tracing.stop(path=trace_filepath)
