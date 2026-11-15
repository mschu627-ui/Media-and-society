import streamlit as st

st.set_page_config(
    page_title="Media and Society",
    page_icon="🎬",
    layout="wide"
)

st.title("Media and Society")
st.write(
    "Find films exploring journalism, propaganda, "
    "public opinion, reputation, and communication ethics."
)

topic = st.selectbox(
    "Choose a communication theme",
    [
        "Journalism",
        "Propaganda",
        "Public opinion",
        "Reputation",
        "Communication ethics"
    ]
)

query = st.text_input(
    "What would you like to explore?",
    placeholder="Example: journalists facing ethical decisions"
)

if st.button("Find films"):
    st.info(
        "Your interface is working. "
        "The TMDB connection comes next."
    )
import requests

st.divider()

if st.button("Test TMDB connection"):
    token = st.secrets.get("TMDB_TOKEN", "")

    if not token:
        st.error("Add TMDB_TOKEN in Streamlit Secrets first.")
    else:
        try:
            response = requests.get(
                "https://api.themoviedb.org/3/movie/11",
                headers={
                    "Authorization": f"Bearer {token.strip()}"
                },
                timeout=15
            )

            if response.status_code == 200:
                movie = response.json()
                st.success("Connected to TMDB!")
                st.write("Test movie:", movie["title"])
            elif response.status_code == 401:
                st.error(
                    "Token rejected. Check your API Read "
                    "Access Token in Streamlit Secrets."
                )
            else:
                st.error(
                    f"TMDB returned status {response.status_code}. "
                    "Try again shortly."
                )

        except requests.RequestException:
            st.error("Connection failed. Try again shortly.")
from tmdb import get_movie

st.divider()
st.subheader("Example film")

try:
    movie = get_movie(314365)

    st.subheader(movie.get("title", "Untitled"))

    year = movie.get("release_date", "")[:4]
    runtime = movie.get("runtime") or "Unknown"
    rating = movie.get("vote_average", 0)

    st.write(
        f"{year} | {runtime} minutes | "
        f"TMDB rating: {rating:.1f}/10"
    )

    genres = ", ".join(
        genre["name"] for genre in movie.get("genres", [])
    )
    st.write("Genres:", genres or "Unavailable")

    st.write(
        movie.get("overview") or "No plot summary available."
    )

    directors = [
        person["name"]
        for person in movie.get("credits", {}).get("crew", [])
        if person.get("job") == "Director"
    ]
    st.write("Director:", ", ".join(directors) or "Unavailable")

except requests.RequestException:
    st.error("Unable to load the film. Please try again.")

except ValueError:
    st.error("Check your TMDB token in Streamlit Secrets.")
from tmdb import search_movies

st.divider()
st.subheader("Search by movie title")

with st.form("movie_title_search"):
    movie_title = st.text_input(
        "Enter a movie title",
        placeholder="Example: Spotlight"
    )
    search_submitted = st.form_submit_button("Search movies")

if search_submitted:
    if not movie_title.strip():
        st.warning("Enter a movie title first.")
    else:
        try:
            results = search_movies(movie_title.strip())

            if not results:
                st.info("No movies found. Try another title.")

            for film in results[:5]:
                title = film.get("title", "Untitled")
                year = film.get("release_date", "")[:4] or "Unknown year"

                st.subheader(f"{title} ({year})")
                st.write(
                    film.get("overview")
                    or "No plot summary available."
                )
                st.caption(f"TMDB movie ID: {film['id']}")

        except requests.RequestException:
            st.error("Search failed. Please try again.")

        except ValueError:
            st.error("Check your TMDB token in Streamlit Secrets.")
