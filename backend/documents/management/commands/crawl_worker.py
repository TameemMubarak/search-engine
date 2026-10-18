from django.core.management.base import BaseCommand
from search_core.database_crawler import DatabaseCrawler


class Command(BaseCommand):
    help = "Run the continuous search-engine crawler"

    def add_arguments(self, parser):
        parser.add_argument("--idle", type=int, default=30)
        parser.add_argument("--delay", type=float, default=1.0)
        parser.add_argument("--depth", type=int, default=3)

    def handle(self, *args, **options):
        crawler = DatabaseCrawler(
            "https://www.tutorialspoint.com/",
            max_pages=1,
            delay=options["delay"],
            max_depth=options["depth"],
        )

        self.stdout.write(self.style.SUCCESS("Starting continuous crawler..."))

        recovered = crawler.frontier.recover_stuck()
        if recovered:
            self.stdout.write(f"Recovered {recovered} interrupted URLs")

        crawler.continuous_crawl(idle_seconds=options["idle"])
