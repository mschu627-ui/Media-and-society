import requests
import streamlit as st

BASE_URL = "https://api.themoviedb.org/3"


@st.cache_data(ttl=3600)
def get_movie(movie_id):
    """Retrieve movie details and cache them for one hour."""
    token = st.secrets.get("TMDB_TOKEN", "").strip()

    if not token:
        raise ValueError("TMDB_TOKEN is missing from Streamlit Secrets.")

    response = requests.get(
        f"{BASE_URL}/movie/{movie_id}",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "append_to_response": "credits,keywords,release_dates",
            "language": "en-US"
        },
        timeout=20
    )

    response.raise_for_status()
    return response.json()
