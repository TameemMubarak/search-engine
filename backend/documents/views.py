from django.http import JsonResponse

from search_core.search_service import SearchService

def search(request):


    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse(
            {
                "error": "Search query is required."
            },
            status=400
        )

    try:
        page = int(
            request.GET.get("page", 1)
        )

        limit = int(
            request.GET.get("limit", 10)
        )

    except ValueError:

        return JsonResponse(
            {
                "error": "Page and limit must be integers."
            },
            status=400
        )

    if page < 1:
        return JsonResponse(
            {
                "error": "Page must be greater than or equal to 1."
            },
            status=400
        )

    limit = min(max(limit, 1), 50)

    try:

        service = SearchService()

        # Get all ranked results first.
        results = service.search(
            query,
            limit=None
        )

    except FileNotFoundError as error:

        return JsonResponse(
            {
                "error": str(error)
            },
            status=500
        )

    total = len(results)

    start = (page - 1) * limit
    end = start + limit

    paginated_results = results[start:end]

    has_previous = page > 1
    has_next = end < total

    return JsonResponse(
        {
            "query": query,
            "page": page,
            "limit": limit,
            "count": len(paginated_results),
            "total": total,
            "has_next": has_next,
            "has_previous": has_previous,
            "results": paginated_results
        }
    )
