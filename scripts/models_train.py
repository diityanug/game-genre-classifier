import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import re
import os
import joblib
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import spacy

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import Pipeline
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import accuracy_score, classification_report, hamming_loss

# =========================
# LOAD DATA
# =========================
print("=== Loading Dataset ===")

if not os.path.exists(config.DATA_FILE_PATH):
    raise FileNotFoundError("Dataset not found")

df = pd.read_csv(config.DATA_FILE_PATH)

target_genres = set(config.ALL_LABELS)

def filter_and_split_genres(genre_str):
    if not isinstance(genre_str, str):
        return []
    genres = [g.strip() for g in genre_str.split(',')]
    return [g for g in genres if g in target_genres]

df['genre_list'] = df['genres'].apply(filter_and_split_genres)
df = df[df['genre_list'].map(len) > 0].reset_index(drop=True)

print("Initial data:", len(df))

# =========================
# LOAD SPACY
# =========================
print("\n=== Loading spaCy ===")
nlp = spacy.load("en_core_web_sm")

for word in config.CUSTOM_STOP_WORDS:
    nlp.vocab[word].is_stop = True

# =========================
# CLEANING
# =========================
def clean_text(text):
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    doc = nlp(text)

    return " ".join([
        token.lemma_
        for token in doc
        if not token.is_stop and len(token) > 2
    ])

print("\n=== Cleaning Text ===")

df['combined_text'] = (df['title'] + " " + df['description']).apply(clean_text)

df['combined_text'] = df['combined_text'].fillna("")
df = df[df['combined_text'].str.strip().astype(bool)].reset_index(drop=True)

print("After cleaning:", len(df))

if len(df) == 0:
    raise ValueError("DATA HABIS SETELAH CLEANING")

# =========================
# LABEL
# =========================
mlb = MultiLabelBinarizer()
y = mlb.fit_transform(df['genre_list'])

print("Classes:", mlb.classes_)

# =========================
# SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    df['combined_text'],
    y,
    test_size=config.TEST_SIZE,
    random_state=config.RANDOM_STATE
)

print("Train size:", len(X_train))
print("Test size:", len(X_test))

# =========================
# MODEL
# =========================
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', OneVsRestClassifier(ComplementNB()))
])

param_grid = {
    'tfidf__ngram_range': [(1, 1), (1, 2)],
    'tfidf__max_df': [0.85, 0.9],
    'clf__estimator__alpha': [0.1, 0.5, 1.0]
}

print("\n=== GridSearch ===")

grid_search = GridSearchCV(
    pipeline,
    param_grid,
    cv=5,
    scoring='f1_micro',
    n_jobs=-1
)

grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_
print("Best Params:", grid_search.best_params_)

# =========================
# EVALUATION
# =========================
y_prob = best_model.predict_proba(X_test)

y_pred = np.zeros((len(X_test), len(mlb.classes_)))

for i, label in enumerate(mlb.classes_):
    probs = y_prob[:, i]
    threshold = config.THRESHOLDS.get(label, config.THRESHOLDS["Default"])
    y_pred[:, i] = (probs >= threshold).astype(int)

print("\n=== Evaluation ===")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Hamming Loss:", hamming_loss(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=mlb.classes_, zero_division=0))

# =========================
# SAVE
# =========================
os.makedirs(config.MODEL_DIR, exist_ok=True)

joblib.dump(best_model, config.MODEL_FILE_PATH)
joblib.dump(mlb, config.MLB_FILE_PATH)

print("\nModel saved.")

# =========================
# INTERACTIVE
# =========================
print("\n=== INTERACTIVE MODE ===")

while True:
    t = input("Title: ")
    if t.lower() in ['exit', 'quit']:
        break

    d = input("Desc : ")

    text = clean_text(t + " " + d)

    probs = best_model.predict_proba([text])[0]  # ✅ FIX FINAL

    sorted_idx = np.argsort(probs)[::-1]

    print("\nResult:")
    found = False

    for idx in sorted_idx:
        if probs[idx] >= config.CONFIDENCE_THRESHOLD:
            found = True
            print(f"{mlb.classes_[idx]} → {probs[idx]*100:.2f}%")

    if not found:
        print("No strong prediction")

    print("-" * 40)