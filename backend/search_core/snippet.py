import re


class SnippetGenerator:

    def __init__(
        self,
        snippet_length=180
    ):
        self.snippet_length = snippet_length

    def generate(
        self,
        content,
        query
    ):

        if not content:
            return ""

        query_terms = [
            term.lower()
            for term in query.split()
            if term.strip()
        ]

        if not query_terms:
            return content[
                :self.snippet_length
            ]

        lower_content = content.lower()

        # Find the first occurrence of
        # any query term.
        match_position = None

        for term in query_terms:

            position = lower_content.find(
                term
            )

            if position != -1:

                if (
                    match_position is None
                    or position < match_position
                ):
                    match_position = position

        # No query term found.
        if match_position is None:

            return content[
                :self.snippet_length
            ]

        half = self.snippet_length // 2

        start = max(
            0,
            match_position - half
        )

        end = min(
            len(content),
            start + self.snippet_length
        )

        snippet = content[start:end]

        if start > 0:
            snippet = "..." + snippet

        if end < len(content):
            snippet += "..."

        return snippet
