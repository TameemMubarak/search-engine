import json
from pathlib import Path


class IndexStorage:

    def __init__(self, file_path="search_index.json"):

        self.file_path = Path(file_path)

    def save(self, index):

        data = {
            "index": index.index,
            "document_lengths": index.document_lengths
        }

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=2
            )

    def load(self):

        if not self.file_path.exists():
            return None

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)