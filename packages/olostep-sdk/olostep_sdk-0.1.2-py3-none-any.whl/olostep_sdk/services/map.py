from typing import Optional


class MapService:
    def __init__(self, client: object) -> None:
        self.client = client

    def get_urls(
        self,
        url: str,
        include_urls: Optional[list[str]] = None,
        exclude_urls: Optional[list[str]] = None,
        top_n: int = 100000,
    ) -> dict:
        payload = {
            "url": url,
            "top_n": top_n,
        }
        if include_urls:
            payload["include_urls"] = include_urls
        if exclude_urls:
            payload["exclude_urls"] = exclude_urls
        return self.client._request("POST", "maps", json=payload)
