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
