from django.http import JsonResponse

from search_core.index_manager import IndexManager
from documents.models import Document


index_manager = IndexManager()


def search_api(request):

    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse(
            {
                "error": "Query parameter 'q' is required."
            },
            status=400
        )

    results = index_manager.search(query)

    response_results = []

    for result in results:

        try:
            document = Document.objects.get(
                id=result["document_id"]
            )

        except Document.DoesNotExist:
            continue

        response_results.append(
            {
                "document_id": document.id,
                "title": document.title,
                "url": document.url,
                "score": round(
                    result["score"],
                    4
                )
            }
        )

    return JsonResponse(
        {
            "query": query,
            "count": len(response_results),
            "results": response_results
        }
    )