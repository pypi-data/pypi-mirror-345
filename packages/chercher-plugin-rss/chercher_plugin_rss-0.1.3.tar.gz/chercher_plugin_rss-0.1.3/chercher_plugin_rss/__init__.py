from typing import Generator
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from markdownify import MarkdownConverter
import feedparser
import httpx
from chercher import Document, hookimpl

markdown_converter = MarkdownConverter()


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.scheme in ["http", "https"] and parsed.netloc)


def fetch_content(client: httpx.Client, uri: str) -> tuple[str, str]:
    response = client.get(uri)
    response.raise_for_status()

    body = response.text
    etag = response.headers.get("ETag", "")
    return body, etag


def parse_feed(client: httpx.Client, content: str) -> Generator[Document, None, None]:
    feed = feedparser.parse(content)
    if feed.bozo:
        return

    for entry in feed.entries:
        uri = entry.link
        if not uri:
            continue

        assert isinstance(uri, str)
        try:
            resp_body, etag = fetch_content(client, uri)
            soup = BeautifulSoup(resp_body, "lxml")
            for tag in soup(
                [
                    "aside",
                    "audio",
                    "canvas",
                    "embed",
                    "footer",
                    "form",
                    "head",
                    "iframe",
                    "img",
                    "nav",
                    "noscript",
                    "picture",
                    "script",
                    "style",
                    "svg",
                    "video",
                ]
            ):
                tag.decompose()

            content = markdown_converter.convert_soup(soup)
            yield Document(
                uri=uri,
                title=entry.get("title", ""),
                body=content,
                hash=etag,
                metadata={},
            )
        except Exception as e:
            print("something went wrong", e)


@hookimpl
def ingest(uri: str, settings: dict) -> Generator[Document, None, None]:
    if not is_valid_url(uri):
        return

    settings = settings.get("rss", {})
    headers = settings.get("headers", {})

    client = httpx.Client(headers=headers)
    try:
        content, _ = fetch_content(client, uri)
        yield from parse_feed(client, content)
    finally:
        client.close()
