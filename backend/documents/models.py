from django.db import models


class Document(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=500)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    content_hash = models.CharField(
        max_length=64,
        blank=True,
        default=""
    )

    def __str__(self):
        return self.title
class CrawlURL(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("crawling", "Crawling"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    url = models.URLField(
        unique=True,
        max_length=2048
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    depth = models.PositiveIntegerField(
        default=0
    )

    attempts = models.PositiveIntegerField(
        default=0
    )

    discovered_at = models.DateTimeField(
        auto_now_add=True
    )

    last_crawled_at = models.DateTimeField(
        null=True,
        blank=True
    )

    next_crawl_at = models.DateTimeField(
        null=True,
        blank=True
    )

    error_message = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.status}: {self.url}"