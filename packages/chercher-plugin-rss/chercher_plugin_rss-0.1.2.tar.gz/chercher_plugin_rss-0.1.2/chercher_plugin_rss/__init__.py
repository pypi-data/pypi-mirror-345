from typing import Generator
from urllib.parse import urlparse
import httpx
import feedparser
from chercher import Document, hookimpl


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
            body, etag = fetch_content(client, uri)
            yield Document(
                uri=uri,
                title=entry.get("title", ""),
                body=body,
                hash=etag,
                metadata={},
            )
        except Exception:
            continue


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
