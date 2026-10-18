import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()

from search_core.index_builder import IndexBuilder
from search_core.index_storage import IndexStorage


builder = IndexBuilder()

index = builder.build()

storage = IndexStorage()

storage.save(index)

print("Index rebuilt successfully.")
print(
    f"Documents indexed: {len(index.document_lengths)}"
)
