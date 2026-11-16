from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyser = SentimentIntensityAnalyzer()


def movie_text(movie):
    """Combine TMDB plot, genres, and keywords."""
    genres = " ".join(
        item["name"] for item in movie.get("genres", [])
    )
    keywords = " ".join(
        item["name"]
        for item in movie.get("keywords", {}).get("keywords", [])
    )
    return " ".join([
        movie.get("overview") or "",
        genres,
        keywords
    ])


def recommend(movies, query, tone="Any", limit=5):
    """Rank relevant films, optionally adding sentiment matching."""
    if not movies or not query.strip():
        return []

    texts = [movie_text(movie) for movie in movies]

    vectoriser = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    try:
        matrix = vectoriser.fit_transform(texts)
    except ValueError:
        return []

    query_vector = vectoriser.transform([query])
    similarities = cosine_similarity(query_vector, matrix)[0]

    targets = {"Positive": 1.0, "Neutral": 0.0, "Negative": -1.0}
    results = []

    for movie, similarity in zip(movies, similarities):
        # Exclude films with no matching topic words.
        if similarity <= 0:
            continue

        plot = movie.get("overview") or ""
        sentiment = analyser.polarity_scores(plot)["compound"]
        score = float(similarity)

        if tone in targets and plot.strip():
            tone_match = 1 - abs(sentiment - targets[tone]) / 2
            # Topic relevance stays the main ranking factor.
            score = 0.8 * score + 0.2 * tone_match

        results.append({
            "movie": movie,
            "score": score,
            "content_score": float(similarity),
            "sentiment": sentiment
        })

    return sorted(
        results,
        key=lambda result: result["score"],
        reverse=True
    )[:limit]
def similar_movies(movies, selected_id, limit=5):
    """Rank other films by shared plot, genre, and keyword text."""
    selected = next(
        (movie for movie in movies if movie["id"] == selected_id),
        None
    )

    if selected is None:
        return []

    candidates = [
        movie for movie in movies
        if movie["id"] != selected_id
    ]

    results = recommend(
        candidates,
        movie_text(selected),
        limit=limit
    )

    # Explain similarities using shared TMDB metadata.
    selected_genres = {
        genre["name"] for genre in selected.get("genres", [])
    }
    selected_keywords = {
        keyword["name"]
        for keyword in selected.get("keywords", {}).get("keywords", [])
    }

    for result in results:
        movie = result["movie"]

        shared_genres = selected_genres.intersection(
            genre["name"] for genre in movie.get("genres", [])
        )
        shared_keywords = selected_keywords.intersection(
            keyword["name"]
            for keyword in movie.get("keywords", {}).get("keywords", [])
        )

        reasons = []

        if shared_genres:
            reasons.append(
                "Shared genres: " + ", ".join(sorted(shared_genres))
            )

        if shared_keywords:
            reasons.append(
                "Shared keywords: "
                + ", ".join(sorted(shared_keywords)[:5])
            )

        result["explanation"] = (
            ". ".join(reasons)
            or "Similar wording in plot summaries and metadata."
        )

    return results
def expand_query(query):
    """Add related terms for five communication themes."""
    theme_terms = {
        "journalism": [
            "journalism", "journalist", "reporter",
            "reporting", "newspaper", "news"
        ],
        "propaganda": [
            "propaganda", "manipulation", "persuasion",
            "disinformation"
        ],
        "public opinion": [
            "public opinion", "politics", "political",
            "election", "campaign"
        ],
        "reputation": [
            "reputation", "scandal", "public relations",
            "image", "publicity"
        ],
        "ethics": [
            "ethics", "ethical", "truth", "deception",
            "dishonesty", "corruption"
        ]
    }

    text = query.casefold()
    extra_terms = []

    for terms in theme_terms.values():
        if any(term in text for term in terms):
            extra_terms.extend(terms)

    return query + " " + " ".join(sorted(set(extra_terms)))
