import re


STOP_WORDS = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "was",
    "were",
    "of",
    "to",
    "in",
    "on",
    "for",
    "and",
    "or",
}


def tokenize(text):
    """
    Convert text into normalized searchable terms.
    """

    text = text.lower()

    tokens = re.findall(r"\b[a-z0-9]+\b", text)

    tokens = [
        token
        for token in tokens
        if token not in STOP_WORDS
    ]

    return tokens