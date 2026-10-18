import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()


from search_core.database_frontier import DatabaseFrontier


frontier = DatabaseFrontier()

frontier.add(
    "https://www.tutorialspoint.com/",
    depth=0
)

frontier.add(
    "https://www.tutorialspoint.com/python/",
    depth=1
)

frontier.add(
    "https://www.tutorialspoint.com/java/",
    depth=1
)

print(
    "Pending:",
    frontier.pending_count()
)

crawl_url = frontier.get_next()

print(
    "Next URL:",
    crawl_url.url
)

frontier.mark_crawling(
    crawl_url
)

print(
    "Status:",
    crawl_url.status
)

frontier.mark_completed(
    crawl_url
)

print(
    "Completed:",
    frontier.completed_count()
)