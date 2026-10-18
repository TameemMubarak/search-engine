import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()

from search_core.index_builder import IndexBuilder


builder = IndexBuilder()

index = builder.build_and_save()

print("================================")
print("INDEX BUILD COMPLETED")
print("================================")

print(
    f"Documents indexed: "
    f"{len(index.document_lengths)}"
)

print(
    f"Unique terms: "
    f"{len(index.index)}"
)

print(
    "Index saved to search_index.json"
)
