# 🎬 CineMatch — Content-Based Movie Recommender System

A content-based movie recommender system built with **Python**, **scikit-learn**, and **Streamlit**. Pick any movie and instantly get 5 similar recommendations — complete with posters, ratings, genres, and overviews fetched live from **TMDB**.

> Built on the [TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata), using cosine similarity over engineered text features (genres, keywords, cast, crew, and overview).

---

## ✨ Features

- 🔎 **Search & select** any movie from a searchable dropdown of ~4,800 titles
- 🤖 **Content-based recommendations** using cosine similarity on vectorized movie metadata
- 🖼️ **Live poster fetching** from the TMDB API
- ⭐ Movie **rating**, **release date**, **genres**, and **overview** shown for the selected movie
- 🎨 Custom dark-themed, responsive Streamlit UI with hover animations
- 🛡️ Resilient to API/network failures (graceful fallback posters, no crashes)
- ⚡ Cached data loading & API calls for fast repeat interactions

---

## 🧠 How It Works

The recommendation engine is **content-based**, meaning it recommends movies similar in *content* rather than relying on other users' ratings (no collaborative filtering).

**Pipeline** (see `notebook86c26b4f17.ipynb` for full details):

1. **Merge datasets** — `tmdb_5000_movies.csv` and `tmdb_5000_credits.csv` are merged on `title`.
2. **Feature selection** — Keep `movie_id`, `title`, `overview`, `genres`, `keywords`, `cast`, and `crew`.
3. **Clean & transform**:
   - Parse stringified JSON columns (`genres`, `keywords`, `cast`, `crew`) using `ast.literal_eval`.
   - Keep the top 3 cast members and only the director from the crew.
   - Strip spaces from multi-word names so `"Sam Worthington"` becomes `"SamWorthington"` (keeps entities distinct during vectorization).
4. **Combine into tags** — `overview + genres + keywords + cast + crew` are merged into a single `tags` column per movie.
5. **Vectorize** — `CountVectorizer` (scikit-learn, `max_features=5000`, English stop words removed) converts each movie's tags into a 5000-dimensional vector.
6. **Compute similarity** — `cosine_similarity` builds a 4806 × 4806 similarity matrix between all movies.
7. **Recommend** — for a selected movie, the 5 most similar movies (highest cosine similarity, excluding itself) are returned.
8. **Serialize** — the processed dataframe and similarity matrix are saved as `movie_list.pkl` and `similarity.pkl` for the app to load instantly (no retraining needed at runtime).

---

## 🗂️ Project Structure

```
cinematch-movie-recommender/
├── app.py                      # Streamlit web app
├── notebook86c26b4f17.ipynb    # Data preprocessing & model building notebook
├── movie_list.pkl              # Preprocessed movie metadata (pickled DataFrame)
├── similarity.pkl              # Precomputed cosine similarity matrix
├── tmdb_5000_movies.csv        # Raw TMDB movies dataset
├── tmdb_5000_credits.csv       # Raw TMDB credits dataset
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- A [TMDB API key](https://www.themoviedb.org/settings/api) (free) for poster/metadata fetching

### Installation

```bash
# Clone the repo
git clone https://github.com/<your-username>/cinematch-movie-recommender.git
cd cinematch-movie-recommender

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install streamlit requests pandas scikit-learn
```

### Set your TMDB API key (recommended)

```bash
export TMDB_API_KEY=your_key_here      # Linux/macOS
$env:TMDB_API_KEY="your_key_here"      # Windows PowerShell
```

### Run the app

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Data processing | pandas, NumPy |
| ML / vectorization | scikit-learn (`CountVectorizer`, `cosine_similarity`) |
| Web app | Streamlit |
| External data | TMDB API |

---

## 📊 Dataset

- **Source:** [TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata) (Kaggle)
- **Size:** ~4,800 movies after cleaning
- **Files used:** `tmdb_5000_movies.csv`, `tmdb_5000_credits.csv`

---

## 🔮 Possible Improvements

- [ ] Switch to `TfidfVectorizer` and compare recommendation quality
- [ ] Add genre-based filtering alongside similarity search
- [ ] Add a "Trending Now" section using TMDB's trending endpoint
- [ ] Include trailer links (YouTube) for each recommended movie
- [ ] Deploy on Streamlit Community Cloud / Hugging Face Spaces

---

## 📄 License

This project is open-sourced for educational purposes. Movie data and posters are provided by [TMDB](https://www.themoviedb.org/) — this product uses the TMDB API but is not endorsed or certified by TMDB.

---

## 🙌 Acknowledgements

- [TMDB](https://www.themoviedb.org/) for the dataset and API
- [Streamlit](https://streamlit.io/) for the app framework
