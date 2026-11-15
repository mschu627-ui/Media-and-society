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
