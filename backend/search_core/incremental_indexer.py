from search_core.inverted_index import InvertedIndex


class IncrementalIndexer:

    def __init__(self, index):
        self.index = index

    def add_document(self, document):
        """
        Add one Django Document to the existing index.
        """

        self.index.add_document(
            document.id,
            document.title,
            document.content
        )

    def update_document(self, document):
        """
        Replace an existing document in the index.
        """

        self.index.remove_document(
            document.id
        )

        self.index.add_document(
            document.id,
            document.title,
            document.content
        )

    def delete_document(self, document_id):
        """
        Remove a document from the index.
        """

        self.index.remove_document(
            document_id
        )
