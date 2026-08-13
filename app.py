import os
import pickle

import requests
import streamlit as st

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------
st.set_page_config(
    page_title="CineMatch — Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Prefer an environment variable over a hardcoded key.
# Set it before running: export TMDB_API_KEY=your_key_here
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "8265bd1679663a7ea12ac168da84d2e8")
PLACEHOLDER_POSTER = "https://via.placeholder.com/500x750/1a1a2e/ffffff?text=No+Poster"


# ------------------------------------------------------------------
# Styling
# ------------------------------------------------------------------
def inject_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #0f0f1a 0%, #14141f 100%);
        }
        .hero {
            text-align: center;
            padding: 1.2rem 0 0.4rem 0;
        }
        .hero h1 {
            font-size: 2.6rem;
            font-weight: 800;
            background: linear-gradient(90deg, #ff4b6e, #ff8f4b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.1rem;
        }
        .hero p {
            color: #9a9ab0;
            font-size: 1.05rem;
        }
        .movie-card {
            background: #1c1c2e;
            border-radius: 14px;
            padding: 10px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            text-align: center;
        }
        .movie-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 10px 25px rgba(255, 75, 110, 0.25);
        }
        .movie-title {
            color: #f2f2f2;
            font-weight: 600;
            font-size: 0.92rem;
            margin-top: 8px;
            min-height: 42px;
        }
        .movie-meta {
            color: #ffb347;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .badge {
            display: inline-block;
            background: #2c2c40;
            color: #cfcfe6;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            margin: 2px 4px 2px 0;
        }
        .section-title {
            color: #f2f2f2;
            font-weight: 700;
            font-size: 1.3rem;
            margin: 1.5rem 0 0.8rem 0;
            border-left: 4px solid #ff4b6e;
            padding-left: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------
# Data loading (cached so pickles aren't reloaded on every interaction)
# ------------------------------------------------------------------
@st.cache_resource
def load_data():
    movies = pickle.load(open("model/movie_list.pkl", "rb"))
    similarity = pickle.load(open("model/similarity.pkl", "rb"))
    return movies, similarity


# ------------------------------------------------------------------
# TMDB fetching (cached + resilient to network/API failures)
# ------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def fetch_movie_details(movie_id):
    """Returns a dict with poster, rating, release date, overview, genres."""
    fallback = {
        "poster": PLACEHOLDER_POSTER,
        "rating": None,
        "release_date": None,
        "overview": "No description available.",
        "genres": [],
    }
    try:
        url = (
            f"https://api.themoviedb.org/3/movie/{movie_id}"
            f"?api_key={TMDB_API_KEY}&language=en-US"
        )
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        return {
            "poster": (
                "https://image.tmdb.org/t/p/w500/" + poster_path
                if poster_path
                else PLACEHOLDER_POSTER
            ),
            "rating": data.get("vote_average"),
            "release_date": data.get("release_date"),
            "overview": data.get("overview") or fallback["overview"],
            "genres": [g["name"] for g in data.get("genres", [])],
        }
    except (requests.RequestException, ValueError):
        return fallback


def recommend(movie, movies, similarity):
    matches = movies[movies["title"] == movie].index
    if len(matches) == 0:
        return []

    index = matches[0]
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
    )

    results = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        details = fetch_movie_details(movie_id)
        results.append({"title": title, **details})
    return results


# ------------------------------------------------------------------
# UI
# ------------------------------------------------------------------
inject_css()

st.markdown(
    """
    <div class="hero">
        <h1>🎬 CineMatch</h1>
        <p>Pick a movie you love — we'll find 5 more you'll probably love too.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    movies, similarity = load_data()
except FileNotFoundError:
    st.error(
        "Couldn't find `model/movie_list.pkl` or `model/similarity.pkl`. "
        "Make sure the `model/` folder is in the same directory as this app."
    )
    st.stop()

movie_list = movies["title"].values

col_select, col_button = st.columns([4, 1])
with col_select:
    selected_movie = st.selectbox(
        "Type or select a movie from the dropdown",
        movie_list,
        label_visibility="collapsed",
        placeholder="Search for a movie...",
    )
with col_button:
    show_button = st.button("🔍 Recommend", type="primary", use_container_width=True)

if show_button:
    if "movie_id" in movies.columns:
        selected_id = movies[movies["title"] == selected_movie].iloc[0].movie_id
        with st.spinner("Loading movie info..."):
            selected_details = fetch_movie_details(selected_id)

        st.markdown('<div class="section-title">You picked</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 3])
        with c1:
            st.image(selected_details["poster"], use_container_width=True)
        with c2:
            st.markdown(f"### {selected_movie}")
            meta_bits = []
            if selected_details["rating"]:
                meta_bits.append(f"⭐ {selected_details['rating']:.1f}/10")
            if selected_details["release_date"]:
                meta_bits.append(f"📅 {selected_details['release_date']}")
            if meta_bits:
                st.markdown(" &nbsp;•&nbsp; ".join(meta_bits))
            if selected_details["genres"]:
                badges = "".join(
                    f'<span class="badge">{g}</span>' for g in selected_details["genres"]
                )
                st.markdown(badges, unsafe_allow_html=True)
            st.write(selected_details["overview"])

    with st.spinner("Finding movies you'll like..."):
        recommendations = recommend(selected_movie, movies, similarity)

    if not recommendations:
        st.warning("Sorry, couldn't find recommendations for that movie.")
    else:
        st.markdown('<div class="section-title">Recommended for you</div>', unsafe_allow_html=True)
        cols = st.columns(5)
        for col, movie in zip(cols, recommendations):
            with col:
                rating_html = (
                    f'<div class="movie-meta">⭐ {movie["rating"]:.1f}</div>'
                    if movie["rating"]
                    else ""
                )
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                st.image(movie["poster"], use_container_width=True)
                st.markdown(
                    f"""
                        <div class="movie-title">{movie['title']}</div>
                        {rating_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
else:
    st.info("👆 Select a movie above and hit **Recommend** to get started.")
