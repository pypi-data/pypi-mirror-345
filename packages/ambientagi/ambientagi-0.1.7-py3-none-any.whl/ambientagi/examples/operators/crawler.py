# pip install ambientagi
from firecrawl import FirecrawlApp  # type: ignore

from ambientagi.providers.firecrawl_integration import FirecrawlWrapper  # type: ignore

app = FirecrawlApp(api_key="")


def main():
    # Replace with your real API key
    api_key = "fc-YOUR_API_KEY"
    fw = FirecrawlWrapper(api_key)

    # 1) Scrape a single URL
    scrape_status = fw.scrape_website("https://firecrawl.dev")
    print("Scrape status:", scrape_status)

    # 2) Crawl a website
    crawl_status = fw.crawl_website("https://firecrawl.dev", limit=10)
    print("Crawl status:", crawl_status)

    # 3) Scrape HackerNews expecting a JSON schema
    articles = fw.scrape_with_schema("https://news.ycombinator.com")
    print("Top articles:", articles)


if __name__ == "__main__":
    main()
