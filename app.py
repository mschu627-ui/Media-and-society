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
from catalogue import load_catalogue

st.divider()
st.subheader("Film collection")

if st.button("Load film collection"):
    try:
        with st.spinner("Loading movie details from TMDB..."):
            movies, missing = load_catalogue()

        st.success(f"Loaded {len(movies)} films.")

        for film in movies:
            year = (film.get("release_date") or "")[:4]
            st.write(f"{film['title']} ({year})")

        if missing:
            st.warning(
                "These films did not load: " + ", ".join(missing)
            )

    except ValueError:
        st.error("Check your TMDB token in Streamlit Secrets.")
from recommender import recommend

st.divider()
st.subheader("Find films for your topic")

with st.form("topic_recommendations"):
    study_topic = st.text_input(
        "Enter a communication topic",
        placeholder="Example: journalism newspaper reporter"
    )

    tone = st.selectbox(
        "Preferred plot-summary sentiment",
        ["Any", "Positive", "Neutral", "Negative"]
    )
        year_range = st.slider(
        "Release year range",
        min_value=1900,
        max_value=2026,
        value=(1900, 2026)
    )

    minimum_rating = st.slider(
        "Minimum TMDB rating",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.5
    )

    maximum_runtime = st.slider(
        "Maximum runtime in minutes",
        min_value=30,
        max_value=300,
        value=300,
        step=5
    )
    submitted = st.form_submit_button("Recommend films")

if submitted:
    if not study_topic.strip():
        st.warning("Enter a topic first.")
    else:
        try:
            with st.spinner("Finding relevant films..."):
                movies, missing = load_catalogue()
                                movies = [
                    film for film in movies
                    if film.get("release_date")
                    and year_range[0]
                    <= int(film["release_date"][:4])
                    <= year_range[1]
                    and (film.get("vote_average") or 0)
                    >= minimum_rating
                    and 0 < (film.get("runtime") or 0)
                    <= maximum_runtime
                ]
                recommendations = recommend(
                    movies,
                    study_topic.strip(),
                    tone=tone
                )

            if missing:
                st.warning(
                    "Some films were unavailable: "
                    + ", ".join(missing)
                )

            if not recommendations:
                st.info(
                    "No matching topic words found. "
                    "Try related words such as "
                    "journalism, reporter, television, or politics."
                )

            for result in recommendations:
                film = result["movie"]
                year = (film.get("release_date") or "")[:4]

                st.subheader(f"{film['title']} ({year})")
                st.write(
                    film.get("overview")
                    or "No plot summary available."
                )
                st.caption(
                    f"Topic similarity: "
                    f"{result['content_score']:.3f} | "
                    f"Plot sentiment: "
                    f"{result['sentiment']:.2f}"
                )

            st.caption(
                "Results come from the current 12-film collection. "
                "Topic similarity measures shared wording. "
                "Plot sentiment estimates the summary's language tone."
            )

        except requests.RequestException:
            st.error("TMDB is unavailable. Please try again.")

        except ValueError:
            st.error("Check your TMDB token in Streamlit Secrets.")
