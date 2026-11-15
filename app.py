import requests
import streamlit as st

from catalogue import load_catalogue
from recommender import recommend

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
    minimum_votes = st.number_input(
        "Minimum number of TMDB votes",
        min_value=0,
        value=0,
        step=100
    )
    maximum_runtime = st.slider(
        "Maximum runtime in minutes",
        min_value=30,
        max_value=300,
        value=300,
        step=5
    )
    language = st.selectbox(
        "Original language",
        ["Any", "English", "French", "Spanish", "Italian", "German"]
    )
    actor_name = st.text_input(
        "Actor name, optional",
        placeholder="Example: Mark Ruffalo"
    )

    director_name = st.text_input(
        "Director name, optional",
        placeholder="Example: Steven Spielberg"
    )
    submitted = st.form_submit_button("Recommend films")

if submitted:
    if not study_topic.strip():
        st.warning("Enter a topic first.")
    else:
        try:
            with st.spinner("Finding relevant films..."):
                movies, missing = load_catalogue()

                filtered_movies = []

                for film in movies:
                    release_date = film.get("release_date") or ""
                    runtime = film.get("runtime") or 0
                    rating = film.get("vote_average") or 0

                    if not release_date:
                        continue

                    year = int(release_date[:4])

                    if not year_range[0] <= year <= year_range[1]:
                        continue

                    if rating < minimum_rating:
                        continue

                    if (film.get("vote_count") or 0) < minimum_votes:
                        continue

                    if not 0 < runtime <= maximum_runtime:
                        continue
                    language_codes = {
                        "English": "en",
                        "French": "fr",
                        "Spanish": "es",
                        "Italian": "it",
                        "German": "de"
                    }

                    if language != "Any":
                        if film.get("original_language") != language_codes[language]:
                            continue
                                        credits = film.get("credits") or {}

                    cast_names = [
                        person.get("name", "").casefold()
                        for person in credits.get("cast", [])
                    ]

                    director_names = [
                        person.get("name", "").casefold()
                        for person in credits.get("crew", [])
                        if person.get("job") == "Director"
                    ]

                    if actor_name.strip():
                        if not any(
                            actor_name.strip().casefold() in name
                            for name in cast_names
                        ):
                            continue

                    if director_name.strip():
                        if not any(
                            director_name.strip().casefold() in name
                            for name in director_names
                        ):
                            continue

                    filtered_movies.append(film)
                recommendations = recommend(
                    filtered_movies,
                    study_topic.strip(),
                    tone=tone
                )

            if missing:
                st.warning(
                    "Some films were unavailable: "
                    + ", ".join(missing)
                )

            if not filtered_movies:
                st.info(
                    "No films meet your filters. "
                    "Try a wider year range, lower rating, "
                    "or longer runtime."
                )

            elif not recommendations:
                st.info(
                    "No matching topic words found. "
                    "Try journalism, reporter, television, or politics."
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
                    f"Runtime: {film.get('runtime')} minutes | "
                    f"TMDB rating: "
                    f"{film.get('vote_average', 0):.1f}/10"
                )

                st.caption(
                    f"Topic similarity: "
                    f"{result['content_score']:.3f} | "
                    f"Plot sentiment: "
                    f"{result['sentiment']:.2f}"
                )

        except requests.RequestException:
            st.error("TMDB is unavailable. Please try again.")

        except ValueError:
            st.error("Check your TMDB token and movie data.")

st.caption(
    "Recommendations use a starting collection of 12 films. "
    "Topic similarity measures shared wording. "
    "Plot sentiment estimates the summary's language tone."
)
