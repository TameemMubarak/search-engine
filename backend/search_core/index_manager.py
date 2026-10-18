from search_core.inverted_index import InvertedIndex
from search_core.index_storage import IndexStorage


class IndexManager:

    def __init__(self, file_path="search_index.json"):

        self.storage = IndexStorage(file_path)

        self.index = InvertedIndex()

        self.load()

    def load(self):

        data = self.storage.load()

        if data is None:

            print("No existing index found.")

            return

        self.index.load_data(data)

        print("Search index loaded.")

    def save(self):

        self.storage.save(
            self.index
        )

        print("Search index saved.")

    def add_document(self, document):

        self.index.add_document(
            document.id,
            document.title,
            document.content
        )

        self.save()

    def update_document(self, document):

        self.index.remove_document(
            document.id
        )

        self.index.add_document(
            document.id,
            document.title,
            document.content
        )

        self.save()

    def delete_document(self, document_id):

        self.index.remove_document(
            document_id
        )

        self.save()

    def search(self, query):

        return self.index.search_query(
            query
        )
