import re
import os
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

RE_CLEAN = re.compile(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.?")
RE_NUMS = re.compile(r"\d+")

try:
    stop = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords', quiet=True)
    stop = set(stopwords.words('english'))

snowball = SnowballStemmer("english")

app = FastAPI(title="Genre Game Multi-Label API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    model_path = os.path.join(os.path.dirname(__file__), "../models/model_multilabel.pkl")
    mlb_path = os.path.join(os.path.dirname(__file__), "../models/mlb.pkl")
    
    model = joblib.load(model_path)
    mlb = joblib.load(mlb_path)
except Exception as e:
    print(f"CRITICAL ERROR: Failed to load components. Error: {e}")
    model = None
    mlb = None

class GameRequest(BaseModel):
    title: str
    description: str

def preprocess_pipeline(text):
    if not isinstance(text, str):
        return ''
    text = RE_CLEAN.sub("", text.lower())
    text = RE_NUMS.sub("", text)
    words = [word for word in text.split() if word not in stop]
    return ' '.join([snowball.stem(w) for w in words])

@app.post("/predict")
async def predict_genre(request: GameRequest):
    if model is None or mlb is None:
        raise HTTPException(status_code=500, detail="Services are currently unavailable.")

    raw_text = f"{request.title} {request.description}"
    raw_words = raw_text.split()

    if any(len(word) > 20 for word in raw_words):
        return {"status": "error", "message": "Input detected as invalid. Please avoid long random strings."}

    if len(raw_words) < 3:
        return {"status": "error", "message": "The description is too short! Please provide at least 3 words."}

    processed_title = preprocess_pipeline(request.title)
    processed_desc = preprocess_pipeline(request.description)
    combined_text = f"{processed_title} {processed_desc}"

    if not combined_text.strip():
        return {"status": "error", "message": "Invalid input. Please use letters and meaningful words."}

    probabilities = model.predict_proba([combined_text])[0]
    
    # Ambil probabilitas tertinggi sebagai acuan "Confidence" utama
    max_prob = max(probabilities) * 100

    if max_prob < 30.0:
        return {
            "status": "error",
            "message": "The Model is confused! This content doesn't clearly match Adventure, Casual, or Sports genres."
        }

    genre_probs = [
        {"genre": g.capitalize(), "probability": round(p * 100, 2)}
        for g, p in zip(mlb.classes_, probabilities)
    ]

    filtered_results = [res for res in genre_probs if res['probability'] >= 15.0]

    return {
        "status": "success",
        "data": sorted(filtered_results, key=lambda x: x['probability'], reverse=True)
    }