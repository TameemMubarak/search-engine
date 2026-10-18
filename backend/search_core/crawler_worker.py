import time

from search_core.database_frontier import DatabaseFrontier
from search_core.database_crawler import DatabaseCrawler


class CrawlerWorker:

    def __init__(
        self,
        seed_url="https://www.tutorialspoint.com/",
        batch_size=5,
        delay=2
    ):
        self.seed_url = seed_url
        self.batch_size = batch_size
        self.delay = delay

        self.frontier = DatabaseFrontier()

    def run_batch(self):

        print("\n==============================")
        print("CRAWLER WORKER STARTED")
        print("==============================")

        crawled = 0

        while crawled < self.batch_size:

            crawl_url = self.frontier.get_next()

            if crawl_url is None:
                print("No pending URLs.")
                break

            print("\nNext URL:")
            print(crawl_url.url)

            self.frontier.mark_crawling(crawl_url)

            try:

                crawler = DatabaseCrawler(
                    self.seed_url,
                    max_pages=1
                )

                response = crawler.fetch(
                    crawl_url.url
                )

                if response is None:
                    raise Exception(
                        "Failed to fetch URL"
                    )

                page = crawler.parse(
                    crawl_url.url,
                    response.text
                )

                document, changed = crawler.save_document(
                    page
                )

                # Discover new URLs
                for link in page.get("links", []):
                    self.frontier.add(
                        link,
                        depth=crawl_url.depth + 1
                    )

                self.frontier.mark_completed(
                    crawl_url
                )

                print(
                    "Completed:",
                    crawl_url.url
                )

                print(
                    "Document changed:",
                    changed
                )

                crawled += 1

                time.sleep(self.delay)

            except Exception as error:

                print(
                    "ERROR:",
                    crawl_url.url
                )

                print(error)

                self.frontier.mark_failed(
                    crawl_url,
                    str(error)
                )

        print("\n==============================")
        print("BATCH COMPLETED")
        print("==============================")
        print("Pages crawled:", crawled)
        print(
            "Pending:",
            self.frontier.pending_count()
        )
        print(
            "Completed:",
            self.frontier.completed_count()
        )


if __name__ == "__main__":

    worker = CrawlerWorker(
        batch_size=5
    )

    worker.run_batch()
