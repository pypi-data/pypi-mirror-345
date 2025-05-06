from firecrawl.firecrawl import FirecrawlApp  # type: ignore

from ambientagi.config.settings import settings
from ambientagi.schemas.schemas import TopArticlesSchema


class AmbientFirecrawl:
    """
    A simple wrapper around FirecrawlApp to expose scraping and crawling in a
    consistent way for AmbientAGI users.
    """

    def __init__(self, agent: dict):
        self.agent = agent
        self.firecrawl_api_key = agent["fireclawer_provider"]
        self.api_key = (
            settings.FIRECRAWL_API_KEY
            if self.firecrawl_api_key is None
            else self.firecrawl_api_key
        )
        self.app = FirecrawlApp(api_key=self.api_key)

    def scrape_website(self, url: str, formats=["markdown", "html"]):
        """
        Scrapes a single URL using Firecrawl.
        """
        return self.app.scrape_url(url, params={"formats": formats})

    def crawl_website(
        self,
        url: str,
        limit: int = 100,
        poll_interval: int = 30,
        formats=["markdown", "html"],
    ):
        """
        Crawls a website up to `limit` pages, scraping each page in `formats`.
        """
        return self.app.crawl_url(
            url,
            params={
                "limit": limit,
                "scrapeOptions": {"formats": formats},
            },
            poll_interval=poll_interval,
        )

    def scrape_with_schema(self, url: str, schema=TopArticlesSchema):
        """
        Scrapes a URL expecting JSON output validated against a Pydantic schema.
        """
        result = self.app.scrape_url(
            url,
            {
                "formats": ["json"],
                "jsonOptions": {"schema": schema.model_json_schema()},
            },
        )
        raw_json = result["json"]
        validated = schema.parse_obj(raw_json)
        return validated
