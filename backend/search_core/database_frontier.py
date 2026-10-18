from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from documents.models import CrawlURL


class DatabaseFrontier:
    RECRAWL_INTERVAL = timedelta(hours=1)

    def add(self, url, depth=0):
        crawl_url, created = CrawlURL.objects.get_or_create(
            url=url,
            defaults={
                "depth": depth,
                "status": "pending",
                "next_crawl_at": timezone.now(),
            },
        )
        return created

    def get_next(self):
        now = timezone.now()

        # Make completed URLs eligible when their recrawl time arrives.
        CrawlURL.objects.filter(
            status="completed",
            next_crawl_at__isnull=False,
            next_crawl_at__lte=now,
        ).update(status="pending")

        with transaction.atomic():
            crawl_url = (
                CrawlURL.objects.select_for_update(skip_locked=True)
                .filter(
                    status="pending",
                    next_crawl_at__lte=now,
                )
                .order_by("discovered_at")
                .first()
            )

            if crawl_url:
                crawl_url.status = "crawling"
                crawl_url.attempts += 1
                crawl_url.save(update_fields=["status", "attempts"])

            return crawl_url

    def mark_crawling(self, crawl_url):
        crawl_url.status = "crawling"
        crawl_url.attempts += 1
        crawl_url.save(update_fields=["status", "attempts"])

    def mark_completed(self, crawl_url):
        now = timezone.now()
        crawl_url.status = "completed"
        crawl_url.last_crawled_at = now
        crawl_url.next_crawl_at = now + self.RECRAWL_INTERVAL
        crawl_url.error_message = ""
        crawl_url.save(
            update_fields=[
                "status",
                "last_crawled_at",
                "next_crawl_at",
                "error_message",
            ]
        )

    def mark_failed(self, crawl_url, error_message):
        crawl_url.status = "failed"
        crawl_url.error_message = error_message
        crawl_url.last_crawled_at = timezone.now()
        crawl_url.save(
            update_fields=["status", "error_message", "last_crawled_at"]
        )

    def retry_failed(self, max_attempts=3):
        now = timezone.now()
        failed_urls = CrawlURL.objects.filter(
            status="failed",
            attempts__lt=max_attempts,
        )

        count = 0
        for crawl_url in failed_urls:
            delay = timedelta(minutes=5 * max(1, crawl_url.attempts))
            if (
                crawl_url.last_crawled_at is not None
                and crawl_url.last_crawled_at + delay <= now
            ):
                crawl_url.status = "pending"
                crawl_url.next_crawl_at = now
                crawl_url.error_message = ""
                crawl_url.save(
                    update_fields=["status", "next_crawl_at", "error_message"]
                )
                count += 1

        return count

    def pending_count(self):
        return CrawlURL.objects.filter(status="pending").count()

    def completed_count(self):
        return CrawlURL.objects.filter(status="completed").count()

    def get_next_pending(self):
        return self.get_next()

    def activate_due_urls(self):
        now = timezone.now()
        return CrawlURL.objects.filter(
            status="completed",
            next_crawl_at__isnull=False,
            next_crawl_at__lte=now,
        ).update(status="pending")

    def recover_stuck(self, minutes=15):
        cutoff = timezone.now() - timedelta(minutes=minutes)
        return CrawlURL.objects.filter(
            status="crawling",
            last_crawled_at__lt=cutoff,
        ).update(
            status="pending",
            next_crawl_at=timezone.now(),
            error_message="Recovered after interrupted crawl",
        )
