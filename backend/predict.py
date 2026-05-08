import os
import re
import joblib
import spacy
import config

# --- LOAD SPACY
try:
    nlp = spacy.load("en_core_web_sm")

    for word in config.CUSTOM_STOP_WORDS:
        nlp.vocab[word].is_stop = True

    cleaning_pattern = re.compile('|'.join(config.CLEANING_REGEX_PATTERNS), re.IGNORECASE)

except OSError:
    raise RuntimeError("spaCy model missing. Run: python -m spacy download en_core_web_sm")

# --- LOAD MODEL
try:
    BASE_DIR = os.path.dirname(__file__)

    model_path = os.path.join(BASE_DIR, config.MODEL_FILE_PATH)
    mlb_path = os.path.join(BASE_DIR, config.MLB_FILE_PATH)

    model = joblib.load(model_path)
    mlb = joblib.load(mlb_path)

except Exception as e:
    print(f"CRITICAL ERROR: Failed to load models. {e}")
    model = None
    mlb = None

# --- PREPROCESSING
def preprocess_pipeline(text: str) -> str:
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = re.sub(r"http\S+", " ", text)
    text = cleaning_pattern.sub(" ", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    doc = nlp(text, disable=['parser', 'ner'])

    return " ".join([
        token.lemma_
        for token in doc
        if not token.is_stop and len(token) > 2
    ])

# --- PREDICTION
def get_prediction(title: str, description: str):
    if model is None or mlb is None:
        return {"status": "error", "code": 500, "message": "ML Services offline."}

    raw_text = f"{title} {description}"
    raw_words = raw_text.split()

    if any(len(word) > 20 for word in raw_words):
        return {"status": "error", "code": 400, "message": "Input invalid (too long words)."}

    if len(raw_words) < 3:
        return {"status": "error", "code": 400, "message": "Description too short."}
    
    combined_raw_text = f"{title} {title} {description}"
    combined_text = preprocess_pipeline(combined_raw_text)

    if not combined_text.strip():
        return {"status": "error", "code": 400, "message": "Invalid input after preprocessing."}

    probabilities = model.predict_proba([combined_text])[0]
    max_prob = max(probabilities)

    if max_prob < 0.20:
        return {
            "status": "error",
            "code": 422,
            "message": "Model is not confident with this input."
        }

    is_dominant = max_prob >= 0.70
    gap_tolerance = 0.05

    tfidf_vectorizer = model.named_steps['tfidf']
    clf_onevsrest = model.named_steps['clf']

    feature_names = tfidf_vectorizer.get_feature_names_out()

    input_vector = tfidf_vectorizer.transform([combined_text])
    present_word_indices = input_vector.nonzero()[1]

    results = []

    for idx, (genre_name, prob) in enumerate(zip(mlb.classes_, probabilities)):

        base_thresh = config.THRESHOLDS.get(
            genre_name,
            config.THRESHOLDS.get("Default", 0.65)
        )

        passed_static = prob >= base_thresh
        is_top = prob == max_prob
        passed_relative = (not is_dominant) and (max_prob - prob <= gap_tolerance) and (prob >= 0.25)

        if passed_static or is_top or passed_relative:
            prob_percent = round(prob * 100, 2)

            nb_estimator = clf_onevsrest.estimators_[idx]
            word_scores = []
        
            if hasattr(nb_estimator, "feature_log_prob_") and nb_estimator.feature_log_prob_.shape[0] > 1:

                for word_idx in present_word_indices:
                    weight = nb_estimator.feature_log_prob_[1][word_idx] * input_vector[0, word_idx]
                    word_scores.append((feature_names[word_idx], weight))

            word_scores.sort(key=lambda x: x[1], reverse=True)
            top_words = [w[0] for w in word_scores[:3]]

            results.append({
                "genre": genre_name,
                "probability": prob_percent,
                "keywords": top_words
            })

    results = sorted(results, key=lambda x: x["probability"], reverse=True)

    if not results:
        return {
            "status": "error",
            "code": 422,
            "message": "No genre passed the confidence threshold."
        }

    return {
        "status": "success",
        "code": 200,
        "data": results[:5]
    }