import os
import re
import sys
import joblib
import spacy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, hamming_loss
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# --- SETUP & LOAD DATA
print("Loading Dataset")
if not os.path.exists(config.DATA_FILE_PATH):
    raise FileNotFoundError(f"Dataset not found at: {config.DATA_FILE_PATH}")

df = pd.read_csv(config.DATA_FILE_PATH)
target_genres = set(config.ALL_LABELS)

def filter_and_split_genres(genre_str):
    if not isinstance(genre_str, str):
        return []
    genres = [g.strip() for g in genre_str.split(",")]
    return [g for g in genres if g in target_genres]

df["genre_list"] = df["genres"].apply(filter_and_split_genres)
df = df[df["genre_list"].map(len) > 0].reset_index(drop=True)

print(f"Initial valid data rows: {len(df)}")

# --- NLP PIPELINE SETUP (spaCy)
print("\nLoading spaCy")
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("spaCy model 'en_core_web_sm' not found. Installing...")
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

for word in config.CUSTOM_STOP_WORDS:
    nlp.vocab[word].is_stop = True

cleaning_pattern = re.compile('|'.join(config.CLEANING_REGEX_PATTERNS), re.IGNORECASE)

def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    text = text.lower()
    text = re.sub(r"http\S+", " ", text)
    text = cleaning_pattern.sub(" ", text) 
    text = re.sub(r"[^a-zA-Z\s]", " ", text) 
    doc = nlp(text, disable=['parser', 'ner'])
    
    return " ".join([
        token.lemma_ for token in doc 
        if not token.is_stop and len(token) > 2
    ])

print("\nCleaning Text")

df["combined_text"] = (df["title"] + " " + df["title"] + " " + df["description"]).apply(clean_text)
df["combined_text"] = df["combined_text"].fillna("")
df = df[df["combined_text"].str.strip().astype(bool)].reset_index(drop=True)

print(f"Data rows after cleaning: {len(df)}")
if len(df) == 0:
    raise ValueError("NO DATA LEFT AFTER CLEANING. Check your cleaning function or dataset.")

# --- ENCODING & SPLITTING
mlb = MultiLabelBinarizer()
y = mlb.fit_transform(df["genre_list"])
plt.figure(figsize=(12, 6))
sns.barplot(x=mlb.classes_, y=y.sum(axis=0), palette="viridis")
plt.xticks(rotation=45, ha="right")
plt.title("Distribusi Genre Game dalam Dataset")
plt.ylabel("Jumlah Game")
plt.tight_layout()
plt.show()

print(f"Classes found ({len(mlb.classes_)}):", mlb.classes_)

X_train, X_test, y_train, y_test = train_test_split(
    df["combined_text"],
    y,
    test_size=config.TEST_SIZE,
    random_state=config.RANDOM_STATE
)

print(f"Train size: {len(X_train)} | Test size: {len(X_test)}")

# --- MODELING & TUNING
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        min_df=3,              
        max_df=0.75,           
        max_features=10000    
    )), 
    ("clf", OneVsRestClassifier(ComplementNB()))
])

param_grid = {
    "tfidf__ngram_range": [(1, 1), (1, 2)],
    "clf__estimator__alpha": [0.05, 0.1, 0.5]
}

print("\nGridSearch Tuning")
grid_search = GridSearchCV(
    pipeline,
    param_grid,
    cv=5,
    scoring="f1_micro",
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_

print("\nBest Params Found:", grid_search.best_params_)

# --- EVALUATION
print("\nEvaluation")
y_prob = best_model.predict_proba(X_test)
y_pred = np.zeros((len(X_test), len(mlb.classes_)))

for i, label in enumerate(mlb.classes_):
    threshold = config.THRESHOLDS.get(label, config.THRESHOLDS.get("Default", 0.4))
    y_pred[:, i] = (y_prob[:, i] >= threshold).astype(int)

print(f"Accuracy (Exact Match) : {accuracy_score(y_test, y_pred):.4f}")
print(f"Hamming Loss           : {hamming_loss(y_test, y_pred):.4f}")

print("\nClassification Report:")
print(classification_report(
    y_test,
    y_pred,
    target_names=mlb.classes_,
    zero_division=0
))
report = classification_report(y_test, y_pred, target_names=mlb.classes_, output_dict=True, zero_division=0)
f1_scores = [report[label]['f1-score'] for label in mlb.classes_]

plt.figure(figsize=(12, 6))
sns.barplot(x=mlb.classes_, y=f1_scores, palette="mako")
plt.xticks(rotation=45, ha="right")
plt.title("F1-Score per Genre (Testing Data)")
plt.ylabel("F1-Score")
plt.ylim(0, 1.0)
plt.tight_layout()
plt.show()

# ---- SAVING MODELS
os.makedirs(config.MODEL_DIR, exist_ok=True)
joblib.dump(best_model, config.MODEL_FILE_PATH)
joblib.dump(mlb, config.MLB_FILE_PATH)
print(f"\nModels successfully saved to {config.MODEL_DIR}")

# ---- INTERACTIVE TESTING
print("\nTESTING MODELS")
print("Type 'exit' or 'quit' on Title to stop.")

while True:
    try:
        t = input("\nGame Title : ")
        if t.lower() in ["exit", "quit"]:
            break
        
        d = input("Description: ")
        text = clean_text(t + " " + t + " " + d)

        if not text.strip():
             print("Result: Input text is too short or removed entirely after cleaning.")
             continue

        probs = best_model.predict_proba([text])[0]
        sorted_idx = np.argsort(probs)[::-1]

        print("Predictions:")
        found_any = False
        
        for idx in sorted_idx:
            label = mlb.classes_[idx]
            threshold = config.THRESHOLDS.get(label, config.THRESHOLDS.get("Default", 0.4))
            
            if probs[idx] >= threshold:
                found_any = True
                print(f"  - {label:<22} → {probs[idx] * 100:>5.2f}% (Threshold: {threshold})")
                
        if not found_any:
            print("(No strong prediction meets the threshold)")
            
    except KeyboardInterrupt:
        break