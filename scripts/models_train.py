import pandas as pd
import re
import os
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import accuracy_score, classification_report, hamming_loss

import matplotlib.pyplot as plt
import seaborn as sns

# DATA PREPARATION
print("=== Loading Master Dataset ===")
file_path = '../data/multigenre_game_datasets.csv'
if not os.path.exists(file_path):
    print(f"Error: {file_path} not found. Please run the collection script first.")
    exit()

df = pd.read_csv(file_path)

target_genres = {'Adventure', 'Sports', 'Casual'}

def filter_and_split_genres(genre_str):
    if not isinstance(genre_str, str): return []
    genres = [g.strip() for g in genre_str.split(',')]
    return [g for g in genres if g in target_genres]

df['genre_list'] = df['genres'].apply(filter_and_split_genres)
df = df[df['genre_list'].map(len) > 0].reset_index(drop=True)

print(f"Total unique games for training: {len(df)}")

# TARGET TRANSFORMATION
print("\n=== Transforming Targets with MultiLabelBinarizer ===")
mlb = MultiLabelBinarizer()
y = mlb.fit_transform(df['genre_list'])

print("Detected Classes:", mlb.classes_)

# PREPROCESSING
nltk.download('stopwords', quiet=True)
stop = set(stopwords.words('english'))
snowball = SnowballStemmer("english")

def clean_text_pipeline(text):
    if not isinstance(text, str): return ''
    text = text.lower()
    text = re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.?", "", text)
    text = re.sub(r"\d+", "", text)
    words = [word for word in text.split() if word not in stop]
    return ' '.join([snowball.stem(w) for w in words])

print("Preprocessing text data...")
df['combined_text'] = (df['title'] + " " + df['description']).apply(clean_text_pipeline)

# MODEL TRAINING WITH PIPELINE & GRIDSEARCH
print("\n=== Training Multi-Label Model ===")

X_train, X_test, y_train, y_test = train_test_split(
    df['combined_text'], y, test_size=0.2, random_state=42
)

pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', OneVsRestClassifier(MultinomialNB()))
])

param_grid = {
    'tfidf__ngram_range': [(1, 1), (1, 2)],
    'tfidf__max_df': [0.85],
    'clf__estimator__alpha': [0.1, 0.5, 1.0] 
}

grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='f1_micro', n_jobs=-1)
grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_
print(f"Best Parameters: {grid_search.best_params_}")

# 5. EVALUATION
y_pred = best_model.predict(X_test)

print("\n=== Multi-Label Evaluation ===")
print(f"Hamming Loss (lower is better): {hamming_loss(y_test, y_pred):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=mlb.classes_))

# SAVING MODELS
print("\n=== Saving Models ===")
os.makedirs('../models', exist_ok=True)
joblib.dump(best_model, "../models/model_multilabel.pkl")
joblib.dump(mlb, "../models/mlb.pkl")
print("Models saved successfully.")

# INTERACTIVE TESTING
def predict_multi_label(title, description):
    text = clean_text_pipeline(title + " " + description)
    probs = best_model.predict_proba([text])[0]
    
    results = [
        {"genre": g, "probability": p * 100} 
        for g, p in zip(mlb.classes_, probs)
    ]
    return sorted(results, key=lambda x: x['probability'], reverse=True)

print("\n=== Quick Test ===")
t = "Elden Ring"
d = "Rise, Tarnished, and be guided by grace to brandish the power of the Elden Ring and become an Elden Lord in the Lands Between."
test_res = predict_multi_label(t, d)
for r in test_res:
    print(f"{r['genre']}: {r['probability']:.2f}%")