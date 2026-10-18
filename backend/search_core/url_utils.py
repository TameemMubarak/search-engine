from urllib.parse import urlparse, urlunparse


def normalize_url(url):
    """
    Convert a URL into a canonical form.
    """

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return None

    if not parsed.netloc:
        return None

    scheme = parsed.scheme.lower()
    domain = parsed.netloc.lower()

    path = parsed.path or "/"

    # Remove fragment
    fragment = ""

    return urlunparse(
        (
            scheme,
            domain,
            path,
            "",
            parsed.query,
            fragment
        )
    )


def get_domain(url):
    """
    Return the domain/host of a URL.
    """

    parsed = urlparse(url)

    return parsed.netloc.lower()


def is_same_domain(url, allowed_domain):
    """
    Check whether a URL belongs to the allowed domain.
    """

    return get_domain(url) == allowed_domain