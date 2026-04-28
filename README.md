# 🎮 Game Genre Classifier (Multi-Label & XAI)

A Full-Stack Machine Learning application designed to predict multiple genres and tags of a game (supporting 15+ categories including Action, RPG, Horror, and Strategy) based on its Title and Description. 

This project utilizes a **Multi-Label Classification** architecture using **TF-IDF**, **Complement Naive Bayes**, and **OneVsRestClassifier** for Natural Language Processing (NLP). It also features **Explainable AI (XAI)** to highlight the specific keywords that influenced the AI's decision, wrapped in an interactive web interface built with React.

---

## 🛠️ Tech Stack

**Frontend:**
* React (via Vite)
* Tailwind CSS
* Lucide React (Icons)

**Backend:**
* Python
* FastAPI & Uvicorn

**Machine Learning & Data Engineering:**
* Scikit-Learn (TF-IDF, ComplementNB, OneVsRestClassifier, MultiLabelBinarizer, GridSearchCV)
* NLTK (Custom Stopwords, Stemming)
* Pandas & Joblib
* Requests & BeautifulSoup4 (Hybrid Scraping via Steam API & SteamSpy)

---

## 📂 Directory Structure

```text
GAME-GENRE-CLASSIFIER/
├── backend/                # API Server (FastAPI) & XAI Logic
│   ├── main.py
├── data/                   # Raw datasets (~15k+ rows) & preprocessing results
├── frontend/               # User Interface (React/Vite)
│   ├── src/
│   │   ├── components/
|   |   |  └── GenreClassifier.jsx
|   |   ├── App.jsx
|   |   └── main.jsx
│   ├── style/
|   |   └── global.css
│   ├── index.html
│   └── package.json
├── models/                 # AI model storage (.pkl & mlb.pkl)
├── scripts/                # Training & Automated scraping scripts
│   ├── collecting_game.py
│   └── models_train.py
└── requirements.txt