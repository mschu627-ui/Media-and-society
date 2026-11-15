import streamlit as st
import requests
from tmdb import search_movies, get_movie

# Starting collection. These films are examples for discussion.
# Recommendations will later rank their TMDB descriptions.
FILMS = [
    ("Spotlight", "2015"),
    ("All the President's Men", "1976"),
    ("The Post", "2017"),
    ("Nightcrawler", "2014"),
    ("Network", "1976"),
    ("Wag the Dog", "1997"),
    ("The Truman Show", "1998"),
    ("The Social Network", "2010"),
    ("Thank You for Smoking", "2005"),
    ("Shattered Glass", "2003"),
    ("Good Night, and Good Luck.", "2005"),
    ("Citizen Kane", "1941"),
]


@st.cache_data(ttl=3600)
def load_catalogue():
    """Find each film by title and year, then fetch its details."""
    movies = []
    missing = []

    for title, year in FILMS:
        try:
            matches = search_movies(title)

            match = next(
                (
                    film for film in matches
                    if (film.get("release_date") or "").startswith(year)
                ),
                None
            )

            if match is None:
                missing.append(title)
                continue

            details = get_movie(match["id"])

            if details["id"] not in {m["id"] for m in movies}:
                movies.append(details)

        except requests.RequestException:
            missing.append(title)

    return movies, missing
