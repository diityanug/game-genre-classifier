import os
import re
import joblib
import spacy
import config

try:
    nlp = spacy.load("en_core_web_sm")
    for word in config.CUSTOM_STOP_WORDS:
        nlp.vocab[word].is_stop = True
except OSError:
    raise RuntimeError("spaCy model missing. Execute: python -m spacy download en_core_web_sm.")

try:
    model_path = os.path.join(os.path.dirname(__file__), config.MODEL_FILE_PATH)
    mlb_path = os.path.join(os.path.dirname(__file__), config.MLB_FILE_PATH)
    
    model = joblib.load(model_path)
    mlb = joblib.load(mlb_path)
except Exception as e:
    print(f"CRITICAL ERROR: Failed to load models. {e}")
    model = None
    mlb = None

def preprocess_pipeline(text: str) -> str:
    if not isinstance(text, str): return ''
    text = text.lower()
    
    for pattern in config.CLEANING_REGEX_PATTERNS:
        text = re.sub(pattern, "", text)
        
    text = re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.?", " ", text)
    text = re.sub(r"\d+", "", text)
    
    doc = nlp(text)
    words = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
    return ' '.join(words)

# Prediction Logic
def get_prediction(title: str, description: str):
    """Main function to be called by FastAPI"""
    if model is None or mlb is None:
        return {"status": "error", "code": 500, "message": "ML Services offline."}

    raw_text = f"{title} {description}"
    raw_words = raw_text.split()

    if any(len(word) > 20 for word in raw_words):
        return {"status": "error", "code": 400, "message": "Input invalid. Avoid long random strings."}

    if len(raw_words) < 3:
        return {"status": "error", "code": 400, "message": "Description too short! Provide at least 3 words."}

    processed_title = preprocess_pipeline(title)
    processed_desc = preprocess_pipeline(description)
    combined_text = f"{processed_title} {processed_desc}"

    if not combined_text.strip():
        return {"status": "error", "code": 400, "message": "Invalid input. Use meaningful words."}

    probabilities = model.predict_proba([combined_text])[0]
    max_prob = max(probabilities) * 100

    if max_prob < 20.0:
        return {
            "status": "error", 
            "code": 422, 
            "message": "The Model is confused! The description does not clearly match any trained genres."
        }

    tfidf_vectorizer = model.named_steps['tfidf']
    clf_onevsrest = model.named_steps['clf']
    feature_names = tfidf_vectorizer.get_feature_names_out()

    input_vector = tfidf_vectorizer.transform([combined_text])
    present_word_indices = input_vector.nonzero()[1]

    filtered_results = []
    
    for idx, (genre_name, prob) in enumerate(zip(mlb.classes_, probabilities)):
        prob_percent = round(prob * 100, 2)
        
        if prob_percent >= config.CONFIDENCE_THRESHOLD:
            nb_estimator = clf_onevsrest.estimators_[idx]
            word_scores = []
            
            for word_idx in present_word_indices:
                word = feature_names[word_idx]
                weight = nb_estimator.feature_log_prob_[1][word_idx] * input_vector[0, word_idx]
                word_scores.append((word, weight))
            
            word_scores.sort(key=lambda x: x[1], reverse=True)
            top_words = [w[0] for w in word_scores[:3]]

            filtered_results.append({
                "genre": genre_name.capitalize(),
                "probability": prob_percent,
                "keywords": top_words
            })

    sorted_top_results = sorted(filtered_results, key=lambda x: x['probability'], reverse=True)[:5]

    return {"status": "success", "code": 200, "data": sorted_top_results}