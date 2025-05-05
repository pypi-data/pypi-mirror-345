from mugennoscraper.controller.scrappers.rawkuma.const import URL_AZ, URL_SEARCH
from mugennoscraper.controller.scrappers.rawkuma.manga import create_manga_instance
from mugennoscraper.controller.scrappers.rawkuma.search import extract_links, extract_titles
from mugennoscraper.controller.scrappers.utils.html import get_html, parse_html
from mugennoshared.model.interfaces import IManga # type: ignore


async def search(query: str) -> tuple[list[str], list[str]]:
    html = await get_html(URL_SEARCH, query)
    soup = await parse_html(html)
    links = await extract_links(soup)
    titles = await extract_titles(soup)
    return links, titles


async def manga(url: str) -> IManga:
    html = await get_html(url, "")
    soup = await parse_html(html)
    return await create_manga_instance(soup)


async def az_list(letter: str, page: int) -> tuple[list[str], list[str]]:
    html = await get_html(URL_AZ, letter)
    soup = await parse_html(html)
    links = await extract_links(soup)
    titles = await extract_titles(soup)
    return links, titles
