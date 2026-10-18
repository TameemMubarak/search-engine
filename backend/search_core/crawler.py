import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()

import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from url_frontier import URLFrontier
from url_utils import (
    normalize_url,
    get_domain,
    is_same_domain
)
from robots import RobotsChecker


class Crawler:

    USER_AGENT = "MySearchEngineBot/0.1"

    # def __init__(self, seed_url, max_pages=10):
    def __init__(
        self,
        seed_url,
        max_pages=10,
        delay=1.0,
        max_retries=3
    ):

        normalized_seed = normalize_url(seed_url)

        if not normalized_seed:
            raise ValueError(
                "Invalid seed URL"
            )

        self.seed_url = normalized_seed

        self.allowed_domain = get_domain(
            normalized_seed
        )

        self.delay = delay
        self.max_retries = max_retries
        self.max_pages = max_pages
        

        self.frontier = URLFrontier()

        self.frontier.add(
            normalized_seed
        )

        self.robots = RobotsChecker(
            normalized_seed,
            self.USER_AGENT
        )

        self.robots.load()

    def fetch(self, url):

        for attempt in range(1, self.max_retries + 1):

            try:

                print(
                    f"Fetching "
                    f"(attempt {attempt}/"
                    f"{self.max_retries})"
                )

                response = requests.get(
                    url,
                    timeout=10,
                    headers={
                        "User-Agent": self.USER_AGENT
                    }
                )

                return response

            except requests.RequestException as error:

                print(
                    f"Request failed: {error}"
                )

                if attempt < self.max_retries:

                    wait_time = 2 ** (attempt - 1)

                    print(
                        f"Retrying in "
                        f"{wait_time} seconds..."
                    )

                    time.sleep(wait_time)

                else:

                    print(
                        "Maximum retries reached."
                    )

        return None
    def parse(self, url, html):

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        title = ""

        if soup.title:

            title = soup.title.get_text(
                strip=True
            )

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        links = []

        for anchor in soup.find_all(
            "a",
            href=True
        ):

            raw_link = anchor["href"]

            absolute_url = urljoin(
                url,
                raw_link
            )

            normalized_link = normalize_url(
                absolute_url
            )

            if not normalized_link:
                continue

            if not is_same_domain(
                normalized_link,
                self.allowed_domain
            ):
                continue

            links.append(
                normalized_link
            )

        return {
            "url": url,
            "title": title,
            "content": text,
            "links": links
        }

    def crawl(self):

        pages_crawled = 0

        while (
            self.frontier.has_pending()
            and pages_crawled < self.max_pages
        ):

            url = self.frontier.next_url()

            print(
                f"\nCrawling: {url}"
            )

            if not self.robots.allowed(url):

                print(
                    "Blocked by robots.txt"
                )

                continue

            try:
                response = self.fetch(url)

                if response is None:
                    continue

                print(
                    f"Status: {response.status_code}"
                )

                

                if response.status_code != 200:

                    print(
                        "Skipping page."
                    )

                    continue

                content_type = response.headers.get(
                    "Content-Type",
                    ""
                ).lower()

                if "text/html" not in content_type:

                    print(
                        f"Skipping non-HTML "
                        f"content: {content_type}"
                    )

                    continue

                page = self.parse(
                    url,
                    response.text
                )

                self.frontier.mark_visited(
                    url
                )

                pages_crawled += 1

                print(
                    f"Title: {page['title']}"
                )

                print(
                    f"Characters: "
                    f"{len(page['content'])}"
                )

                print(
                    f"Links found: "
                    f"{len(page['links'])}"
                )

                for link in page["links"]:
                    
                    self.frontier.add(link)
                time.sleep(self.delay)
            except requests.RequestException as error:

                print(
                    f"Request failed: {error}"
                )

        print("\nCrawl completed.")

        print(
            f"Pages crawled: "
            f"{pages_crawled}"
        )

        print(
            f"Visited URLs: "
            f"{self.frontier.visited_count()}"
        )

        print(
            f"Pending URLs: "
            f"{self.frontier.pending_count()}"
        )


if __name__ == "__main__":

    crawler = Crawler(
        "https://www.tutorialspoint.com/",
        max_pages=5
    )

    crawler.crawl()