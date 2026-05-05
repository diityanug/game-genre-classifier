import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import re
import os
import joblib
import config
import spacy

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import Pipeline
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import accuracy_score, classification_report, hamming_loss, multilabel_confusion_matrix

# DATA PREPARATION
print("=== Loading Master Dataset ===")
if not os.path.exists(config.DATA_FILE_PATH):
    print(f"Error: {config.DATA_FILE_PATH} not found. Please run the collection script first.")
    exit()

df = pd.read_csv(config.DATA_FILE_PATH)

target_genres = set(config.ALL_LABELS)

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
print("\n=== Initializing spaCy Lemmatizer ===")
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("spaCy model missing. Execute: python -m spacy download en_core_web_sm.")
    exit()

custom_stop_words = config.CUSTOM_STOP_WORDS
for word in custom_stop_words:
    nlp.vocab[word].is_stop = True

def clean_text_advanced(text):
    if not isinstance(text, str): return ''
    
    text = text.lower()
    
    for pattern in config.CLEANING_REGEX_PATTERNS:
        text = re.sub(pattern, "", text)
        
    text = re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.?", " ", text)
    
    text = re.sub(r"\d+", "", text)

    doc = nlp(text)
    
    cleaned_words = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and not token.is_space]

    return ' '.join(cleaned_words)

print("Text preprocessing pipeline (lemmatization + custom regex)...")

raw_texts = (df['title'] + " " + df['description']).tolist()
cleaned_texts = []

for doc in nlp.pipe(raw_texts, disable=["ner", "parser"]):
    text = doc.text.lower()
    for pattern in config.CLEANING_REGEX_PATTERNS:
        text = re.sub(pattern, "", text)
    text = re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.?", " ", text)
    text = re.sub(r"\d+", "", text)
    
    temp_doc = nlp.make_doc(text)
    
    cleaned_words = [token.lemma_ for token in nlp(text) if not token.is_stop and not token.is_punct and not token.is_space]
    cleaned_texts.append(' '.join(cleaned_words))

df['combined_text'] = cleaned_texts

# MODEL TRAINING WITH PIPELINE & GRIDSEARCH
print("\n=== Training Multi-Label Model ===")

X_train, X_test, y_train, y_test = train_test_split(
    df['combined_text'], y, 
    test_size=config.TEST_SIZE, 
    random_state=config.RANDOM_STATE
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
os.makedirs(config.MODEL_DIR, exist_ok=True)
joblib.dump(best_model, config.MODEL_FILE_PATH)
joblib.dump(mlb, config.MLB_FILE_PATH)
print(f"Models saved successfully in '{config.MODEL_DIR}/'")

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
    
    processed_text = clean_text_advanced(t_input + " " + d_input)
    
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
        
        if prob_percent >= config.CONFIDENCE_THRESHOLD:
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
        print(f"No strong genre detected (Confidence < {config.CONFIDENCE_THRESHOLD}%).")
        
    print("-" * 50 + "\n")