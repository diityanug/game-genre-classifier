import pandas as pd
import numpy as np
import re
import os
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import Pipeline
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import accuracy_score, classification_report, hamming_loss, multilabel_confusion_matrix

import matplotlib.pyplot as plt
import seaborn as sns

# DATA PREPARATION
print("=== Loading Master Dataset ===")
file_path = '../data/game_genre_datasets.csv' 
if not os.path.exists(file_path):
    print(f"Error: {file_path} not found. Please run the collection script first.")
    exit()

df = pd.read_csv(file_path)

target_genres = {
    'Action', 'Adventure', 'RPG', 'Strategy', 'Simulation', 
    'Sports', 'Racing', 'Casual', 'Massively Multiplayer', 
    'Horror', 'Shooter', 'Survival', 'Open World', 'Sci-fi', 'Fantasy'
}

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

custom_game_words = {
    'game', 'games', 'play', 'player', 'players', 'playing', 
    'experience', 'world', 'feature', 'features', 'new', 'time', 
    'make', 'take', 'get', 'like', 'one'
}
stop = stop.union(custom_game_words)

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
    ('clf', OneVsRestClassifier(ComplementNB())) 
])

param_grid = {
    'tfidf__ngram_range': [(1, 1), (1, 2)],
    'tfidf__max_df': [0.85, 0.90],
    'clf__estimator__alpha': [0.1, 0.5, 1.0] 
}

print("Searching for the best parameters...")
grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='f1_micro', n_jobs=-1)
grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_
print(f"Best Parameters: {grid_search.best_params_}")

# EVALUATION
y_pred = best_model.predict(X_test)

print("\n=== Multi-Label Evaluation ===")
acc = accuracy_score(y_test, y_pred)
print(f"Exact Match Accuracy: {acc * 100:.2f}%")
print(f"Hamming Loss (lower is better): {hamming_loss(y_test, y_pred):.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=mlb.classes_, zero_division=0))

print("\nDisplaying Multi-Label Confusion Matrices...")
mcm = multilabel_confusion_matrix(y_test, y_pred)

num_classes = len(mlb.classes_)
cols = 4
rows = int(np.ceil(num_classes / cols))

fig, axes = plt.subplots(rows, cols, figsize=(16, 4 * rows))
axes = axes.flatten()

for i, (label, matrix) in enumerate(zip(mlb.classes_, mcm)):
    sns.heatmap(matrix, annot=True, fmt='d', cmap='Blues', ax=axes[i],
                xticklabels=['False', 'True'], yticklabels=['False', 'True'], cbar=False)
    axes[i].set_title(f'Genre: {label}')
    axes[i].set_ylabel('Actual')
    axes[i].set_xlabel('Predicted')

for j in range(num_classes, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()

# SAVING MODELS
print("\n=== Saving Models ===")
os.makedirs('../models', exist_ok=True)
joblib.dump(best_model, "../models/model_multilabel.pkl")
joblib.dump(mlb, "../models/mlb.pkl")
print("Models saved successfully in '../models/'")

# INTERACTIVE TESTING
print("\n" + "="*50)
print("       INTERACTIVE GENRE PREDICTOR")
print("="*50)
print("Type 'exit' or 'quit' in the title to stop.\n")

while True:
    t_input = input("Insert Game Title      : ")
    if t_input.lower() in ['exit', 'quit']:
        print("Testing finished. Goodbye!")
        break
        
    d_input = input("Insert Game Description: ")
    
    processed_text = clean_text_pipeline(t_input + " " + d_input)
    
    probs = best_model.predict_proba([processed_text])[0]
    
    tfidf_vectorizer = best_model.named_steps['tfidf']
    clf_onevsrest = best_model.named_steps['clf']
    feature_names = tfidf_vectorizer.get_feature_names_out()
    
    input_vector = tfidf_vectorizer.transform([processed_text])
    present_word_indices = input_vector.nonzero()[1]

    print("\n--- Analysis Result ---")
    results_found = False
    
    sorted_indices = np.argsort(probs)[::-1]
    
    for idx in sorted_indices:
        prob_percent = probs[idx] * 100
        
        if prob_percent >= 15.0:
            results_found = True
            genre_name = mlb.classes_[idx]
            
            nb_estimator = clf_onevsrest.estimators_[idx]
            word_scores = []
            for word_idx in present_word_indices:
                weight = nb_estimator.feature_log_prob_[1][word_idx] * input_vector[0, word_idx]
                word_scores.append((feature_names[word_idx], weight))
            
            word_scores.sort(key=lambda x: x[1], reverse=True)
            top_k = [w[0] for w in word_scores[:3]]
            
            print(f"[{genre_name.upper()}] Confidence: {prob_percent:.2f}%")
            if top_k:
                print(f"   Key Factors: {', '.join(top_k)}")

    if not results_found:
        print("No strong genre detected (Confidence < 15%).")
        
    print("-" * 50 + "\n")