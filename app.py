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
