import time
from typing import Optional

from olostep_sdk.enums import OloStepContry, OlostepParser


class BatchService:
    """
    A service for interacting with the Olostep Batch API.
    """

    def __init__(self, client: "OlostepClient") -> None:
        """
        Initialize the BatchService.

        Args:
            client (OlostepClient): Authenticated OlostepClient instance.
        """
        self.client = client

    def start_batch(
        self,
        items: list[dict],
        parser: OlostepParser | None = None,
        country: OloStepContry | None = OloStepContry.US,
    ) -> str:
        """
        Start a new batch job with multiple URLs.

        Args:
            items (list[dict]): List of URLs with optional metadata.
            parser (str): The parser to apply for structured extraction.
            country (str): Country code to route the scraping through.

        Returns:
            str: The batch ID.
        """
        payload = {
            "items": items,
            "parser": parser,
            "country": country,
        }
        response = self.client._request("POST", "batches", json=payload)
        return response.get("id", "")

    def get_status(self, batch_id: str) -> str:
        """
        Get the current status of a batch.

        Args:
            batch_id (str): The ID of the batch.

        Returns:
            str: The batch status ("in_progress", "completed", etc.).
        """
        return self.client._request("GET", f"batches/{batch_id}").get("status", "")

    def wait_until_complete(self, batch_id: str, interval: int = 10) -> None:
        """
        Wait until the given batch has completed.

        Args:
            batch_id (str): The ID of the batch.
            interval (int): Time in seconds to wait between status checks.
        """
        while True:
            if self.get_status(batch_id) == "completed":
                break
            time.sleep(interval)

    def get_items(self, batch_id: str) -> list[dict]:
        """
        Get all items processed by a completed batch.

        Args:
            batch_id (str): The ID of the batch.

        Returns:
            list[dict]: A list of scraped item metadata.
        """
        return self.client._request("GET", f"batches/{batch_id}/items").get("items", [])

    def retrieve_content(
        self,
        retrieve_id: str,
        formats: Optional[list[str]] = None,
    ) -> dict:
        """
        Retrieve scraped content by retrieve ID.

        Args:
            retrieve_id (str): The ID used to fetch content.
            formats (list[str], optional): Formats like 'json', 'markdown', 'html'.

        Returns:
            dict: The retrieved content.
        """
        return self.client._request(
            "GET",
            "retrieve",
            params={
                "retrieve_id": retrieve_id,
                "formats": formats or ["markdown", "json"],
            },
        )
