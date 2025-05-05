from olostep_sdk.request_wrapper import make_request

from .services.batch import BatchService
from .services.crawl import CrawlService
from .services.map import MapService
from .services.scrape import ScrapeService


class OlostepClient:
    def __init__(
        self, api_token: str, base_url: str = "https://api.olostep.com/v1"
    ) -> None:
        if not api_token:
            raise ValueError("API token is required.")
        self.api_token = api_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        self.scrape = ScrapeService(self)
        self.batch = BatchService(self)
        self.crawl = CrawlService(self)
        self.map = MapService(self)

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return make_request(method, url, headers=self.headers, **kwargs)
