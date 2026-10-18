import math


def calculate_title_boost(
    title_frequency,
    boost=2.0
):
    """
    Calculate additional relevance for
    terms appearing in the document title.
    """

    return title_frequency * boost

def calculate_idf(total_documents, document_frequency):
    """
    Calculate smoothed inverse document frequency.
    """

    return math.log(
        (total_documents + 1)
        / (document_frequency + 1)
    ) + 1


def calculate_tf(term_frequency):
    """
    Calculate term frequency.
    """

    return term_frequency


def calculate_tfidf(term_frequency, total_documents, document_frequency):
    """
    Calculate TF-IDF score.
    """

    tf = calculate_tf(term_frequency)

    idf = calculate_idf(
        total_documents,
        document_frequency
    )

    return tf * idf


def calculate_bm25(
    term_frequency,
    document_frequency,
    total_documents,
    document_length,
    average_document_length,
    k1=1.2,
    b=0.75
):
    """
    Calculate the BM25 score for one term in one document.
    """

    idf = calculate_idf(
        total_documents,
        document_frequency
    )

    length_normalization = (
        1 - b
        + b * (document_length / average_document_length)
    )

    numerator = term_frequency * (k1 + 1)

    denominator = (
        term_frequency
        + k1 * length_normalization
    )

    score = idf * (numerator / denominator)

    return score

