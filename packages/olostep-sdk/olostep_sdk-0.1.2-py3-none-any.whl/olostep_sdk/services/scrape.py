from typing import Optional

from ..enums import Format


class ScrapeService:
    def __init__(self, client: object) -> None:
        self.client = client

    def scrape(
        self,
        url_to_scrape: str,
        formats: Optional[list[Format]] = None,
        country: str = "US",
        parser: Optional[str] = None,
        **kwargs,
    ) -> dict:
        payload = {
            "url_to_scrape": url_to_scrape,
            "formats": formats or [Format.HTML, Format.MARKDOWN],
            "country": country,
        }
        if parser:
            payload["parser"] = parser
        payload.update(kwargs)
        return self.client._request("POST", "scrapes", json=payload)
