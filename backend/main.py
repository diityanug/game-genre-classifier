from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI()

# Load model & vectorizer
model = joblib.load("model.pkl")
vectorizer = joblib.load("tfidf.pkl")

class InputText(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "Game Genre Classifier API is running"}

@app.post("/predict")
def predict(data: InputText):
    # Transform text
    vec = vectorizer.transform([data.text])

    # Get probabilities
    probs = model.predict_proba(vec)[0]
    genres = model.classes_

    # Combine genre + probability
    result = [
        {"genre": genre, "probability": float(prob)}
        for genre, prob in zip(genres, probs)
    ]

    # Sort & ambil top 3
    result = sorted(result, key=lambda x: x["probability"], reverse=True)[:3]

    return {"predictions": result}