from collections import defaultdict
from search_core.tokenizer import tokenize
from search_core.ranking import (calculate_tfidf, calculate_bm25,calculate_title_boost)
from search_core.query_processor import QueryProcessor

class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(dict)
        self.document_lengths = {}
# old add document definition
    # def add_document(self, document_id, text):
    #     tokens = tokenize(text)

    #     # Save document length for ranking normalization
    #     self.document_lengths[document_id] = len(tokens)

    #     for position, token in enumerate(tokens):
    #         # Normalize to lowercase so search matching works properly
    #         normalized_token = token.lower()

    #         if document_id not in self.index[normalized_token]:
    #             self.index[normalized_token][document_id] = {
    #                 "frequency": 0,
    #                 "positions": []
    #             }

    #         self.index[normalized_token][document_id]["frequency"] += 1
    #         self.index[normalized_token][document_id]["positions"].append(position)


    def add_document(self, document_id, title, content):

        # if the doc is already present in the index do not add it.
        if document_id in self.document_lengths:
            self.remove_document(document_id)

        title_tokens = tokenize(title)
        body_tokens = tokenize(content)

        all_tokens = title_tokens + body_tokens

        self.document_lengths[document_id] = len(all_tokens)

        title_positions = {}

        for position, token in enumerate(title_tokens):

            normalized_token = token.lower()

            if normalized_token not in title_positions:
                title_positions[normalized_token] = []

            title_positions[normalized_token].append(position)

        for position, token in enumerate(all_tokens):

            normalized_token = token.lower()

            if document_id not in self.index[normalized_token]:

                self.index[normalized_token][document_id] = {
                    "frequency": 0,
                    "title_frequency": 0,
                    "body_frequency": 0,
                    "positions": []
                }

            posting = self.index[normalized_token][document_id]

            posting["frequency"] += 1
            posting["positions"].append(position)

        for token, positions in title_positions.items():

            posting = self.index[token][document_id]

            posting["title_frequency"] += len(positions)

        for token in set(token.lower() for token in body_tokens):

            if token in self.index:

                posting = self.index[token][document_id]

                posting["body_frequency"] += body_tokens.count(token)
    def average_document_length(self):
        """Calculate the average token length across all stored documents."""
        if not self.document_lengths:
            return 0

        return sum(
            self.document_lengths.values()
        ) / len(self.document_lengths)

    def search(self, term):
        term = term.lower()
        return self.index.get(term, {})

    def search_and(self, terms):
        """Return a set of document IDs containing ALL terms."""
        if not terms:
            return set()

        # Get the document IDs for the first term
        result = set(self.search(terms[0]).keys())

        # Intersect with subsequent terms; short-circuit if the set becomes empty
        for term in terms[1:]:
            if not result:
                break
            result.intersection_update(self.search(term).keys())

        return result

    def search_or(self, terms):
        """Return a set of document IDs containing ANY of the terms."""
        result = set()
        for term in terms:
            result.update(self.search(term).keys())
        return result

    def search_ranked(self, term):
        """Rank documents for a single term using TF-IDF."""
        postings = self.search(term)

        total_documents = len(self.document_lengths)
        document_frequency = len(postings)

        results = []

        for document_id, posting in postings.items():
            score = calculate_tfidf(
                posting["frequency"],
                total_documents,
                document_frequency
            )

            results.append({
                "document_id": document_id,
                "score": score
            })

        results.sort(
            key=lambda result: result["score"],
            reverse=True
        )

        return results

    def search_bm25(self, term):
        """Rank documents for a single term using BM25."""
        postings = self.search(term)

        total_documents = len(self.document_lengths)
        document_frequency = len(postings)

        if total_documents == 0:
            return []

        average_length = self.average_document_length()
        results = []

        for document_id, posting in postings.items():
            document_length = self.document_lengths[document_id]

            score = calculate_bm25(
                term_frequency=posting["frequency"],
                document_frequency=document_frequency,
                total_documents=total_documents,
                document_length=document_length,
                average_document_length=average_length
            )

            results.append({
                "document_id": document_id,
                "score": score
            })

        results.sort(
            key=lambda result: result["score"],
            reverse=True
        )

        return results

    def search_multi_bm25(self, query):
        """
        Search multiple terms and rank documents using BM25.
        """

        query_terms = tokenize(query)

        if not query_terms:
            return []

        total_documents = len(self.document_lengths)

        if total_documents == 0:
            return []

        average_length = self.average_document_length()

        scores = defaultdict(float)

        for term in query_terms:

            postings = self.search(term)

            if not postings:
                continue

            document_frequency = len(postings)

            for document_id, posting in postings.items():

                document_length = self.document_lengths[document_id]

                bm25_score = calculate_bm25(
                    term_frequency=posting["frequency"],
                    document_frequency=document_frequency,
                    total_documents=total_documents,
                    document_length=document_length,
                    average_document_length=average_length
                )

                title_boost = calculate_title_boost(
                    posting["title_frequency"]
                )

                scores[document_id] += (
                    bm25_score + title_boost
                )

        results = [
            {
                "document_id": document_id,
                "score": score
            }
            for document_id, score in scores.items()
        ]

        results.sort(
            key=lambda result: result["score"],
            reverse=True
        )

        return results


    
    def search_phrase(self, phrase):
        """
        Return documents where all phrase terms
        occur consecutively and in order.
        """

        terms = tokenize(phrase)

        if not terms:
            return set()

        first_postings = self.search(terms[0])

        matching_documents = set(first_postings.keys())

        for term in terms[1:]:
            postings = self.search(term)

            matching_documents.intersection_update(
                postings.keys()
            )

        results = set()

        for document_id in matching_documents:

            first_positions = first_postings[
                document_id
            ]["positions"]

            valid = False

            for start_position in first_positions:

                phrase_found = True

                for offset, term in enumerate(terms[1:], start=1):

                    positions = self.search(term)[
                        document_id
                    ]["positions"]

                    if start_position + offset not in positions:
                        phrase_found = False
                        break

                if phrase_found:
                    valid = True
                    break

            if valid:
                results.add(document_id)

        return results
    def load_data(self, data):
        self.index = defaultdict(dict)

        for term, postings in data["index"].items():

            for document_id, posting in postings.items():

                self.index[term][int(document_id)] = posting

        self.document_lengths = {
            int(document_id): length
            for document_id, length
            in data["document_lengths"].items()
        }

        # Definition <==> Search_Query_Phraser
    
    def search_query(self, query):
        """
        Execute a parsed user query against the inverted index.
        """

        processor = QueryProcessor()

        parsed = processor.process(query)

        query_type = parsed["type"]

        # Empty query
        if query_type == "empty":
            return []

        # Normal multi-term query
        if query_type == "terms":

            return self.search_multi_bm25(
                query
            )

        # Exact phrase query
        if query_type == "phrase":

            document_ids = self.search_phrase(
                parsed["phrase"]
            )

            return [
                {
                    "document_id": document_id,
                    "score": 1.0
                }
                for document_id in document_ids
            ]

        # Boolean query
        if query_type == "boolean":

            left_terms = parsed["left"]
            right_terms = parsed["right"]

            if parsed["operator"] == "AND":

                document_ids = self.search_and(
                    left_terms + right_terms
                )

            else:

                document_ids = self.search_or(
                    left_terms + right_terms
                )

            return self.rank_documents(
                document_ids,
                left_terms + right_terms
            )

        return self.search_ranked_query(
                query
            )



    def rank_documents(
        self,
        document_ids,
        query_terms
    ):
        """
        Rank an existing candidate set using BM25.
        """

        if not document_ids:
            return []

        if not query_terms:
            return []

        total_documents = len(
            self.document_lengths
        )

        if total_documents == 0:
            return []

        average_length = (
            self.average_document_length()
        )

        scores = defaultdict(float)

        for term in query_terms:

            postings = self.search(term)

            if not postings:
                continue

            document_frequency = len(
                postings
            )

            for document_id in document_ids:

                posting = postings.get(
                    document_id
                )

                if posting is None:
                    continue

                document_length = (
                    self.document_lengths[
                        document_id
                    ]
                )

                score = calculate_bm25(
                    term_frequency=posting[
                        "frequency"
                    ],
                    document_frequency=document_frequency,
                    total_documents=total_documents,
                    document_length=document_length,
                    average_document_length=average_length
                )

                scores[document_id] += score

        results = [
            {
                "document_id": document_id,
                "score": score
            }
            for document_id, score
            in scores.items()
        ]

        results.sort(
            key=lambda result: result["score"],
            reverse=True
        )

        return results
    def search_phrase_ranked(self, phrase, phrase_boost=3.0):
        """
        Search an exact phrase and rank matching documents.
        """

        matching_documents = self.search_phrase(phrase)

        if not matching_documents:
            return []

        query_terms = tokenize(phrase)

        results = []

        for document_id in matching_documents:

            phrase_score = 0

            first_postings = self.search(query_terms[0])

            positions = first_postings[
                document_id
            ]["positions"]

            for start_position in positions:

                phrase_found = True

                for offset, term in enumerate(
                    query_terms[1:],
                    start=1
                ):

                    term_positions = self.search(term)[
                        document_id
                    ]["positions"]

                    if start_position + offset not in term_positions:

                        phrase_found = False
                        break

                if phrase_found:

                    phrase_score += phrase_boost

            results.append({
                "document_id": document_id,
                "score": phrase_score
            })

        results.sort(
            key=lambda result: result["score"],
            reverse=True
        )

        return results

    def search_ranked_query(self, query):
        """
        Unified ranking pipeline.
        Combines BM25, title relevance, and phrase relevance.
        """

        query_terms = tokenize(query)

        if not query_terms:
            return []

        total_documents = len(self.document_lengths)

        if total_documents == 0:
            return []

        average_length = self.average_document_length()

        scores = defaultdict(float)

        # -------------------------
        # 1. BM25 + TITLE BOOST
        # -------------------------

        for term in query_terms:

            postings = self.search(term)

            if not postings:
                continue

            document_frequency = len(postings)

            for document_id, posting in postings.items():

                document_length = self.document_lengths[
                    document_id
                ]

                bm25_score = calculate_bm25(
                    term_frequency=posting["frequency"],
                    document_frequency=document_frequency,
                    total_documents=total_documents,
                    document_length=document_length,
                    average_document_length=average_length
                )

                title_boost = calculate_title_boost(
                    posting["title_frequency"],
                    boost=2.0
                )

                scores[document_id] += (
                    bm25_score + title_boost
                )

        # -------------------------
        # 2. PHRASE BOOST
        # -------------------------

        if len(query_terms) > 1:

            phrase_documents = self.search_phrase(
                query
            )

            for document_id in phrase_documents:

                # Controlled phrase boost.
                scores[document_id] += 3.0

        # -------------------------
        # 3. FINAL RESULTS
        # -------------------------

        results = [
            {
                "document_id": document_id,
                "score": score
            }
            for document_id, score in scores.items()
        ]

        results.sort(
            key=lambda result: result["score"],
            reverse=True
        )

        return results
    def remove_document(self, document_id):
        """
        Remove a document and all of its postings
        from the inverted index.
        """

        terms_to_delete = []

        for term, postings in self.index.items():

            if document_id in postings:
                del postings[document_id]

            if not postings:
                terms_to_delete.append(term)

        for term in terms_to_delete:
            del self.index[term]

        if document_id in self.document_lengths:
            del self.document_lengths[document_id]