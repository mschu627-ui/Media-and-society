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
    ("Broadcast News", "1987"),
    ("Ace in the Hole", "1951"),
    ("A Face in the Crowd", "1957"),
    ("Sweet Smell of Success", "1957"),
    ("The Insider", "1999"),
    ("Frost/Nixon", "2008"),
    ("She Said", "2022"),
    ("Official Secrets", "2019"),
    ("The Report", "2019"),
    ("Denial", "2016"),
    ("Quiz Show", "1994"),
    ("The Great Hack", "2019"),
    ("The Social Dilemma", "2020"),
    ("The Lives of Others", "2006"),
    ("The Conversation", "1974"),
    ("No", "2012"),
    ("The China Syndrome", "1979"),
    ("State of Play", "2009"),
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
