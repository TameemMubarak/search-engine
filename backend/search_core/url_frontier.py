from collections import deque


class URLFrontier:

    def __init__(self):
        self.pending = deque()
        self.visited = set()

    def add(self, url):
        """
        Add a URL if we have not already
        visited or queued it.
        """

        if url in self.visited:
            return False

        if url in self.pending:
            return False

        self.pending.append(url)

        return True

    def next_url(self):
        """
        Get the next URL to crawl.
        """

        if not self.pending:
            return None

        return self.pending.popleft()

    def mark_visited(self, url):
        """
        Mark a URL as successfully processed.
        """

        self.visited.add(url)

    def has_pending(self):
        return len(self.pending) > 0

    def pending_count(self):
        return len(self.pending)

    def visited_count(self):
        return len(self.visited)