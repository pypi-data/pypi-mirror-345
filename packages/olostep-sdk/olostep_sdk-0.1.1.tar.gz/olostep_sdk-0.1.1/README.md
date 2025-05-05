# Olostep SDK

A lightweight Python SDK for interacting with the Olostep scraping, crawling, and batching API.

## 🚀 Installation

Install from PyPI:

    pip install olostep-sdk

## 🧰 Features

- Scrape single URLs with different parsers
- Batch process multiple items
- Crawl starting from a URL
- Retrieve and parse content in multiple formats (JSON, Markdown, etc.)

## 🔑 Getting Started

First, initialize the SDK with your API token:

    from olostep_sdk import OlostepClient
    from olostep_sdk.services.scrape import ScrapeService
    from olostep_sdk.enums import OlostepParser, Format

    client = OlostepClient(api_token="your-api-token")
    scraper = ScrapeService(client)

### 🔍 Scrape a URL

    result = scraper.scrape(
        url="https://example.com",
        parser=OlostepParser.GOOGLE_SEARCH
    )
    print(result)

### 📦 Start a Batch

    from olostep_sdk.services.batch import BatchService

    batch = BatchService(client)
    batch_id = batch.start_batch([
        {"url": "https://example1.com"},
        {"url": "https://example2.com"}
    ])
    batch.wait_until_complete(batch_id)
    items = batch.get_items(batch_id)

### 🌐 Crawl a Website

    from olostep_sdk.services.crawl import CrawlService

    crawler = CrawlService(client)
    crawl_id = crawler.start_crawl("https://example.com")
    crawler.wait_until_complete(crawl_id)
    results = crawler.get_items(crawl_id)

## 📄 Formats and Parsers

    from olostep_sdk.enums import Format, OlostepParser

    Format.MARKDOWN
    Format.JSON

    OlostepParser.GOOGLE_SEARCH
    OlostepParser.BASIC

## 🧪 Running Tests

    python -m unittest discover -s tests

## 📬 License

This project is licensed under the MIT License.