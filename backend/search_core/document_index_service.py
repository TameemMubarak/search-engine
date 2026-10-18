from search_core.index_manager import IndexManager


class DocumentIndexService:

    def __init__(self):
        self.manager = IndexManager()

    def index_document(self, document):
        self.manager.add_document(document)

    def update_document(self, document):
        self.manager.update_document(document)

    def delete_document(self, document_id):
        self.manager.delete_document(document_id)



