from documents.models import Document
from search_core.inverted_index import InvertedIndex


class IndexBuilder:

    def __init__(self):
        self.index = InvertedIndex()

    def build(self):
        """
        Build the complete inverted index
        from all documents in the database.
        """

        documents = Document.objects.all()

        for document in documents:

            self.index.add_document(
                document.id,
                document.title,
                document.content
            )

        return self.index