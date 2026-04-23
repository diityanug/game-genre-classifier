# 🎮 Game Genre AI Classifier

A Full-Stack Machine Learning application designed to predict the genre of a game (Adventure, Casual, or Sport) based on its Title and Description. 

This project utilizes **TF-IDF** and **Multinomial Naive Bayes** for Natural Language Processing (NLP) and text classification, wrapped in an interactive web interface built with React.

---

## 🛠️ Tech Stack

**Frontend:**
* React (via Vite)
* Tailwind CSS
* Lucide React (Icons)

**Backend:**
* Python
* FastAPI & Uvicorn

**Machine Learning:**
* Scikit-Learn (TF-IDF, Naive Bayes, Pipeline, GridSearchCV)
* NLTK (Stopwords, Stemming)
* Pandas & Joblib

---

## 📂 Directory Structure

```text
GAME-GENRE-CLASSIFIER/
├── backend/                # API Server (FastAPI)
│   ├── main.py
│   └── requirements.txt
├── data/                   # Raw datasets & preprocessing results
├── frontend/               # User Interface (React/Vite)
│   ├── src/
│   ├── index.html
│   └── package.json
├── models/                 # AI model storage (.pkl)
└── scripts/                # Training & scraping scripts
    ├── models_train.py
    └── scraping_game.py