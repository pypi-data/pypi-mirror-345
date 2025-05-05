from bs4 import BeautifulSoup


async def extract_titles(soup: BeautifulSoup) -> list[str]:
    return [
        title.get_text(strip=True)
        for title in soup.select(".tt")  # ou ".bigor .tt" para ser mais específico
    ]


async def extract_links(soup: BeautifulSoup) -> list[str]:
    return [
        str(a["href"])
        for a in soup.select("div.bs > div.bsx > a")
        if a.has_attr("href")
    ]


async def extract_covers(soup: BeautifulSoup) -> list[str]:
    return [
        str(img["src"])  # No HTML fornecido, as imagens usam "src" não "data-src"
        for img in soup.select(".limit img")  # Seleciona imagens dentro da div .limit
        if img.has_attr("src")
    ]


async def extract_scores(soup: BeautifulSoup) -> list[str]:
    return [
        score.get_text(strip=True)
        for score in soup.select(
            ".numscore"
        )  # A pontuação está na div com classe numscore
    ]


async def extract_chapters(soup: BeautifulSoup) -> list[str]:
    return [
        chapter.get_text(strip=True)
        for chapter in soup.select(".epxs")  # Os capítulos estão na div com classe epxs
    ]
