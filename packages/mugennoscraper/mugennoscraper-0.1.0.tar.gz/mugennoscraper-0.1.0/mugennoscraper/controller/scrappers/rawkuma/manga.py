import numpy as np
from bs4 import BeautifulSoup
import mugennoscraper.controller.scrappers.rawkuma.manga as manga
from mugennoshared.model.genre import Genre # type: ignore
from mugennoshared.model.manga import Manga # type: ignore
from mugennoshared.model.interfaces import IManga # type: ignore


async def create_manga_instance(soup: BeautifulSoup) -> IManga:
    return Manga(
        title=await manga.extract_title(soup),
        url=await manga.extract_url(soup),
        synopsis=await manga.extract_synopsis(soup),
        cover=await manga.extract_cover(soup),
        language=await manga.extract_language(soup),
        status=await manga.extract_status(soup),
        rating=await manga.extract_rating(soup),
        last_chapter=await manga.extract_last_chapter(soup),
        release_date=await manga.extract_release_date(soup),
        last_update=await manga.extract_last_update(soup),
        author=await manga.extract_author(soup),
        artists=await manga.extract_artists(soup),
        serialization=await manga.extract_serialization(soup),
        genres=[
            Genre[genre.upper().replace(" ", "_")]
            for genre in await manga.extract_genres(soup)
        ],
        embedding=np.random.rand(384).astype(np.float32),
    )


async def extract_title(soup: BeautifulSoup) -> str:
    title = soup.select_one(".entry-title")
    return title.get_text(strip=True) if title else ""


async def extract_url(soup: BeautifulSoup) -> str:
    url = soup.select_one("link[rel='canonical']")
    return str(url["href"]) if url and url.has_attr("href") else ""


async def extract_synopsis(soup: BeautifulSoup) -> str:
    synopsis = soup.select_one(".entry-content-single")
    return synopsis.get_text(strip=True) if synopsis else ""


async def extract_cover(soup: BeautifulSoup) -> str:
    cover = soup.select_one(".thumb img")
    return str(cover["src"]) if cover and cover.has_attr("src") else ""


async def extract_language(soup: BeautifulSoup) -> str:
    # Assumindo que o idioma é inglês (não está explícito no HTML)
    return "No Implementation"


async def extract_status(soup: BeautifulSoup) -> str:
    status = soup.select_one(".imptdt i")
    return status.get_text(strip=True) if status else ""


async def extract_rating(soup: BeautifulSoup) -> float:
    rating = soup.select_one(".num")
    return float(rating.get_text(strip=True)) if rating else 0.0


async def extract_last_chapter(soup: BeautifulSoup) -> float:
    chapter = soup.select_one(".epcurlast")
    if chapter:
        try:
            return float(chapter.get_text(strip=True).replace("Chapter ", ""))
        except ValueError:
            pass
    return 0.0


async def extract_release_date(soup: BeautifulSoup) -> str:
    date = soup.select_one("time[itemprop='datePublished']")
    if date and date.has_attr("datetime"):
        return str(date["datetime"]).split("T")[0]
    return ""


async def extract_last_update(soup: BeautifulSoup) -> str:
    date = soup.select_one("time[itemprop='dateModified']")
    if date and date.has_attr("datetime"):
        return str(date["datetime"]).split("T")[0]
    return ""


async def extract_author(soup: BeautifulSoup) -> str:
    # Encontra o label "Author" e pega o span seguinte
    for div in soup.select("div.fmed"):
        if "Author" in div.get_text():
            author = div.select_one("span")
            return author.get_text(strip=True) if author else ""
    return ""


async def extract_artists(soup: BeautifulSoup) -> str:
    # Encontra o label "Artist" e pega o span seguinte
    for div in soup.select("div.fmed"):
        if "Artist" in div.get_text():
            artist = div.select_one("span")
            return artist.get_text(strip=True) if artist else ""
    return ""


async def extract_serialization(soup: BeautifulSoup) -> str:
    """Extrai a serialização do manga"""
    # Procura pelo label "Serialization" e pega o span ou link seguinte
    for div in soup.select("div.fmed"):
        if "Serialization" in div.get_text():
            serialization = div.select_one("span, a")  # Pega span ou link
            return serialization.get_text(strip=True) if serialization else "-"
    return "-"  # Retorna "-" como padrão quando não encontrado


async def extract_genres(soup: BeautifulSoup) -> list[str]:
    genres = []
    genre_tags = soup.select(".mgen a")
    for tag in genre_tags:
        genres.append(tag.get_text(strip=True))
    return genres
