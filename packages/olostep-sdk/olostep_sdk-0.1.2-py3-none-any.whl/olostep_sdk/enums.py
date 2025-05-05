from enum import Enum


class OlostepParser(str, Enum):
    """Predefined parsers for Olostep structured scraping."""

    GOOGLE_SEARCH = "@olostep/google-search"
    AMAZON_IT_PRODUCT = "@olostep/amazon-it-product"

    # Reserved parsers (may require contact)
    LINKEDIN_PROFILE = "@olostep/linkedin-profile"
    TIKTOK_DATA = "@olostep/tiktok-data"
    GOOGLE_NEWS = "@olostep/google-news"
    GOOGLE_MAPS = "@olostep/google-maps"

    def __str__(self) -> str:
        return self.value


class OlostepBatchStatus(str, Enum):
    """Predefined batch statuses for Olostep."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    def __str__(self) -> str:
        return self.value


class OloStepContry(str, Enum):
    """Predefined countries for Olostep."""

    US = "US"
    CA = "CA"
    GB = "GB"
    DE = "DE"
    FR = "FR"
    IT = "IT"
    ES = "ES"
    NL = "NL"
    PL = "PL"
    BR = "BR"
    IN = "IN"
    AU = "AU"
    JP = "JP"
    RU = "RU"

    def __str__(self) -> str:
        return self.value


class Format(str, Enum):
    """Valid response formats for scraping/crawling."""

    HTML = "html"
    MARKDOWN = "markdown"

    def __str__(self) -> str:
        return self.value
