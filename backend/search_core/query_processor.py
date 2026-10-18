import re

from search_core.tokenizer import tokenize


class QueryProcessor:

    def process(self, query):

        query = query.strip()

        if not query:
            return {
                "type": "empty",
                "terms": [],
                "raw_query": query
            }

        # Exact phrase:
        # "python programming"
        if (
            len(query) >= 2
            and query.startswith('"')
            and query.endswith('"')
        ):

            phrase = query[1:-1].strip()

            return {
                "type": "phrase",
                "terms": tokenize(phrase),
                "raw_query": query,
                "phrase": phrase
            }

        # Boolean query
        boolean_match = re.match(
            r"^(.+?)\s+(AND|OR)\s+(.+)$",
            query,
            re.IGNORECASE
        )

        if boolean_match:

            left = boolean_match.group(1)
            operator = boolean_match.group(2).upper()
            right = boolean_match.group(3)

            return {
                "type": "boolean",
                "operator": operator,
                "left": tokenize(left),
                "right": tokenize(right),
                "raw_query": query
            }

        # Normal multi-term query
        return {
            "type": "terms",
            "terms": tokenize(query),
            "raw_query": query
        }
