import time
from typing import Optional


class CrawlService:
    def __init__(self, client: object) -> None:
        self.client = client

    def start_crawl(
        self,
        start_url: str,
        max_pages: int = 100,
        include_urls: Optional[list[str]] = None,
        exclude_urls: Optional[list[str]] = None,
        max_depth: Optional[int] = None,
        include_external: bool = False,
        parser: Optional[str] = None,
        search_query: Optional[str] = None,
        top_n: Optional[int] = None,
    ) -> dict:
        payload = {
            "start_url": start_url,
            "max_pages": max_pages,
            "include_urls": include_urls or ["/**"],
            "exclude_urls": exclude_urls,
            "max_depth": max_depth,
            "include_external": include_external,
        }
        if parser:
            payload["parser"] = parser
        if search_query:
            payload["search_query"] = search_query
        if top_n:
            payload["top_n"] = top_n
        return self.client._request("POST", "crawls", json=payload)

    def get_crawl_info(self, crawl_id: str) -> dict:
        return self.client._request("GET", f"crawls/{crawl_id}")

    def get_crawl_status(self, crawl_id: str) -> str:
        """
        Get the current status of a crawl.

        Args:
            crawl_id (str): The ID of the crawl.

        Returns:
            str: The crawl status ("in_progress", "completed", etc.).
        """
        return self.client._request("GET", f"crawls/{crawl_id}").get("status", "")

    def wait_until_complete(self, crawl_id: str, interval: int = 5) -> None:
        while True:
            if self.get_crawl_info(crawl_id).get("status") == "completed":
                break
            time.sleep(interval)

    def get_pages(
        self, crawl_id: str, cursor: Optional[int] = None, limit: Optional[int] = None
    ) -> dict:
        params = {}
        if cursor is not None:
            params["cursor"] = cursor
        if limit:
            params["limit"] = limit
        return self.client._request("GET", f"crawls/{crawl_id}/pages", params=params)

    def search_pages(self, crawl_id: str, search_query: str) -> dict:
        return self.client._request(
            "GET", f"crawls/{crawl_id}/list", params={"search_query": search_query}
        )

    def retrieve_content(
        self, retrieve_id: str, formats: Optional[list[str]] = None
    ) -> dict:
        params = {"retrieve_id": retrieve_id}
        if formats:
            params["formats"] = formats
        return self.client._request("GET", "retrieve", params=params)
