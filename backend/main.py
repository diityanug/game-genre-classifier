from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import os

nltk.download('stopwords', quiet=True)
stop = set(stopwords.words('english'))
snowball = SnowballStemmer("english")

def preprocess_pipeline(text):
    if not isinstance(text, str): return ''
    text = re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.?", "", text.lower())
    text = re.sub(r"\d+", "", text)
    words = [word for word in text.split() if word not in stop]
    return ' '.join([snowball.stem(w) for w in words])

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Model AI
model_path = os.path.join(os.path.dirname(__file__), "../models/model.pkl")
model = joblib.load(model_path)

class GameRequest(BaseModel):
    title: str
    description: str

@app.post("/predict")
def predict_genre(request: GameRequest):
    combined_text = preprocess_pipeline(request.title) + " " + preprocess_pipeline(request.description)
    probabilities = model.predict_proba([combined_text])[0]
    
    genre_probs = [
        {"genre": g.capitalize(), "probability": round(p * 100, 2)} 
        for g, p in zip(model.classes_, probabilities)
    ]
    return sorted(genre_probs, key=lambda x: x['probability'], reverse=True)