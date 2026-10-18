
from django.urls import path

from documents.views import search


urlpatterns = [
    path(
        "search/",
        search,
        name="search-api"
    ),
]
