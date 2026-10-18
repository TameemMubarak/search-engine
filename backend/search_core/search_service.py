import os

from documents.models import Document

from search_core.snippet import SnippetGenerator
from search_core.inverted_index import InvertedIndex
from search_core.index_storage import IndexStorage


class SearchService:

    def __init__(
        self,
        index_path="search_index.json"
    ):

        self.storage = IndexStorage(
            index_path
        )

        self.index = InvertedIndex()

        data = self.storage.load()

        if data is None:
            raise FileNotFoundError(
                "Search index does not exist. "
                "Build the index first."
            )

        self.index.load_data(data)
        self.snippet_generator = SnippetGenerator()

    def search(
        self,
        query,
        limit=10
    ):

        if not query or not query.strip():
            return []

        ranked_results = (
            self.index.search_query(query)
            # self.index.search_multi_bm25(query)
        )

        results = []
        if limit is not None:
            ranked_results = ranked_results[:limit]

        for result in ranked_results:
        # for result in ranked_results[:limit]:

            document_id = result[
                "document_id"
            ]

            try:

                document = Document.objects.get(
                    id=document_id
                )

            except Document.DoesNotExist:

                continue

            snippet = self.snippet_generator.generate(
                document.content,
                query
            )

            results.append({
                "document_id": document.id,
                "title": document.title,
                "url": document.url,
                "score": round(
                    result["score"],
                    4
                ),
                "snippet": snippet
            })


# old result format
            # results.append({
            #     "document_id": document.id,
            #     "title": document.title,
            #     "url": document.url,
            #     "score": round(
            #         result["score"],
            #         4
            #     )
            # })

        return results