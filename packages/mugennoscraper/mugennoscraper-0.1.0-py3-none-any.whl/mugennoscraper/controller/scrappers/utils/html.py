from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import requests # type: ignore


TIMEOUT = 60

async def parse_html(html: str) -> BeautifulSoup:
    print("Parsing HTML...", html[:0])
    return BeautifulSoup(html, "html.parser")


async def get_html(url: str, query: str) -> str:
    encoded_query = quote_plus(query)
    url = url + encoded_query
    print("Fetching...", url)

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    response = requests.get(url, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()  # Levanta erro se não for 200

    return response.text
