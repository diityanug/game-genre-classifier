import pandas as pd
import re
import ast
import os
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import SnowballStemmer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd

genres_data = [
    ('adventure', 'adventure_games'),
    ('casual', 'casual_games'),
    ('sport', 'sports_games')
]

processed_games = {}

# process, filter, and save each genre
for genre, file_prefix in genres_data:
    df = pd.read_csv(f'../data/{file_prefix}_data.csv')
    
    df['genres'] = df['genres'].str.lower()
    df_filtered = df[df['genres'].str.contains(genre, na=False)].copy()
    df_filtered['genres'] = genre
    
    df_filtered.to_csv(f'../data/{file_prefix}_genre.csv', index=False)
    processed_games[genre] = df_filtered
    
    print(f"Successful processing datasets : {genre} (Total: {len(df_filtered)} game)")
    print(f"=== Top 3 Dataset: {genre.capitalize()} ===")
    print(df_filtered.head(3), "\n")

# merge data directly from dictionary
combined_games = pd.concat(processed_games.values(), ignore_index=True)
combined_games = combined_games.drop_duplicates(subset='title')

combined_games.to_csv('../data/combined_games_genre.csv', index=False)

# show final statistics
print("=== Final Combined Datasets ===")
print(f"Total games that have been collected: {len(combined_games)}")
print("\nNumber of games per genre:")
print(combined_games['genres'].value_counts())

## PREPROCESSING ##
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

print("\n=== Starting Preprocessing ===")

# case folding & cleaning
def clean_text(text):
    if not isinstance(text, str):
        return ''
    text = text.lower()
    text = re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.?", "", text)
    text = re.sub(r"\d+", "", text)
    return text

combined_games['title_clean'] = combined_games['title'].apply(clean_text)
combined_games['genre_clean'] = combined_games['genres'].apply(clean_text)
combined_games['description_clean'] = combined_games['description'].apply(clean_text)

# stopword removal
stop = set(stopwords.words('english'))

def remove_stopwords(text):
    return ' '.join([word for word in text.split() if word not in stop])

combined_games['title_clean_StopWord'] = combined_games['title_clean'].apply(remove_stopwords)
combined_games['genre_clean_StopWord'] = combined_games['genre_clean'].apply(remove_stopwords)
combined_games['description_clean_StopWord'] = combined_games['description_clean'].apply(remove_stopwords)

# tokenizing
combined_games['title_tokens'] = combined_games['title_clean_StopWord'].apply(lambda x: re.findall(r'\b\w+\b', x))
combined_games['description_tokens'] = combined_games['description_clean_StopWord'].apply(lambda x: re.findall(r'\b\w+\b', x))

# stemming using snowball
snowball = SnowballStemmer("english")
combined_games['title_snowball'] = combined_games['title_tokens'].apply(lambda tokens: [snowball.stem(token) for token in tokens])
combined_games['description_snowball'] = combined_games['description_tokens'].apply(lambda tokens: [snowball.stem(token) for token in tokens])

combined_games.to_csv('../data/preprocessing_result.csv', index=False)

print("Preprocessing completed! Data saved to '../data/preprocessing_result.csv'")
print("\n=== Sample Preprocessing Results (Stemming) ===")
print(combined_games[['title_snowball', 'description_snowball']].head(3))

## WEIGHTING USING TF-IDF ##
print("\n=== Getting Started with Weighting using TF-IDF ===")

# Combining text
combined_games['title_text'] = combined_games['title_snowball'].apply(lambda x: ' '.join(x) if isinstance(x, list) else '')
combined_games['desc_text'] = combined_games['description_snowball'].apply(lambda x: ' '.join(x) if isinstance(x, list) else '')

combined_games['combined_text'] = combined_games['title_text'] + " " + combined_games['desc_text']
combined_games['combined_text'] = combined_games['combined_text'].fillna('')

print("Sample combined text:")
print(combined_games['combined_text'].head(3))

# initialize TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer(
    max_df=0.85,      
    min_df=2,         
    ngram_range=(1, 2)
)

# transform text into a vector matrix
tfidf_matrix = tfidf_vectorizer.fit_transform(combined_games['combined_text'])
print(f"\nTF-IDF Matrix Shape: {tfidf_matrix.shape}")

# displays the term with the highest score in a given document.
feature_names = tfidf_vectorizer.get_feature_names_out()

def display_top_terms(tfidf_row, features, top_n=10):
    nz_indices = tfidf_row.nonzero()[1]
    nz_scores = tfidf_row.data
    
    if len(nz_scores) == 0:
        return []
        
    sorted_idx = nz_scores.argsort()[::-1]
    top_indices = nz_indices[sorted_idx[:top_n]]
    top_scores = nz_scores[sorted_idx[:top_n]]
    
    return [(features[i], score) for i, score in zip(top_indices, top_scores)]

doc_id = min(10, tfidf_matrix.shape[0] - 1)
top_terms = display_top_terms(tfidf_matrix[doc_id], feature_names)

print(f"\nTop terms for index documents-{doc_id}:")
for term, score in top_terms:
    print(f"- {term}: {score:.4f}")

# showing the 20 words with the highest TF-IDF weights globally (entire corpus)
term_sums = tfidf_matrix.sum(axis=0).A1
terms_freq_df = pd.DataFrame({
    'term': feature_names,
    'tfidf_sum': term_sums
}).sort_values(by='tfidf_sum', ascending=False)

print("\nTop 20 global terms:")
print(terms_freq_df.head(20).to_string(index=False))

## IMPLEMENT NAIVE BAYES ##
print("\n=== Getting Started with Naive Bayes Implementation ===")

text_column = 'combined_text'
label_column = 'genre_clean_StopWord'

X = combined_games[text_column]
y = combined_games[label_column]

# transform text to TF-IDF vector (model only)
tfidf_vectorizer_nb = TfidfVectorizer()
X_tfidf = tfidf_vectorizer_nb.fit_transform(X)

print(f"The text data has been converted into a TF-IDF matrix with shapes: {X_tfidf.shape}")

# splitting dataset (80% training, 20% testing)
X_train, X_test, y_train, y_test = train_test_split(
    X_tfidf, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Total training data : {X_train.shape[0]}")
print(f"Total testing data : {X_test.shape[0]}")

# initialization and training of Naive Bayes model
model = MultinomialNB()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

# model evaluation
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# showing Confusion Matrix
conf_matrix = confusion_matrix(y_test, y_pred)
labels_classes = model.classes_

print("\nConfusion Matrix:")
print(conf_matrix)

# plotting confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=labels_classes, yticklabels=labels_classes)
plt.xlabel("Predicted Labels")
plt.ylabel("True Labels")
plt.title("Confusion Matrix - Naive Bayes")
print("\nDisplaying the Confusion Matrix plot... (Close the plot window to continue/end the program)")
plt.show()


## IMPROVE MODEL USING PIPELINE AND GRIDSEARCHCV ##
print("\n=== Improve Model using Pipeline & GridSearchCV ===")

# splitting text data directly
X_train_text, X_test_text, y_train, y_test = train_test_split(
    combined_games['combined_text'],
    combined_games['genre_clean_StopWord'],
    test_size=0.2,
    random_state=42,
    stratify=combined_games['genre_clean_StopWord']
)

# def pipeline
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('nb', MultinomialNB())
], memory=None)

# grid param
param_grid = {
    'tfidf__ngram_range': [(1, 1), (1, 2)],
    'tfidf__max_df': [0.7, 0.85],
    'tfidf__min_df': [2, 5],
    'nb__alpha': [0.5, 1.0]
}

# train with GridSearchCV
print("Currently searching for the best parameters (this may take a while)...")
grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
grid_search.fit(X_train_text, y_train)

best_params = grid_search.best_params_
print("\nBest Parameters:")
for key, value in best_params.items():
    print(f" - {key}: {value}")
print(f"Best Cross-Validation Accuracy: {grid_search.best_score_:.4f}")

y_pred = grid_search.predict(X_test_text)
print(f"\nTest Accuracy: {accuracy_score(y_test, y_pred):.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# showing confusion matrix
conf_matrix = confusion_matrix(y_test, y_pred, labels=grid_search.classes_)
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=grid_search.classes_, yticklabels=grid_search.classes_)
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix - GridSearchCV')
print("\nDisplaying the Confusion Matrix (GridSearchCV) plot... Close the window to continue.")
plt.show()

print("\n=== Saving Model ===")
os.makedirs('../models', exist_ok=True)
best_model = grid_search.best_estimator_
joblib.dump(best_model, "../models/model.pkl")
print("Model saved successfully in'../models/model.pkl'")


## TESTING INTERACTIVE PROBABILITY ##
def preprocess_pipeline(text):
    if not isinstance(text, str):
        return ''
    text = text.lower()
    text = re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.?", "", text)
    text = re.sub(r"\d+", "", text)
    words = [word for word in text.split() if word not in stop]
    return ' '.join([snowball.stem(w) for w in words])

def predict_genre_probabilities(title, description):
    combined_text = preprocess_pipeline(title) + " " + preprocess_pipeline(description)
    probabilities = grid_search.predict_proba([combined_text])[0]
    
    genre_probs = [{"genre": g.capitalize(), "probability": p * 100} for g, p in zip(grid_search.classes_, probabilities)]
    return sorted(genre_probs, key=lambda x: x['probability'], reverse=True)

print("\n=== Interactive Probability Prediction Testing ===")
print("Type 'exit' in the Title field to stop the program..\n")

while True:
    title_input = input("Insert Game Title      : ")
    if title_input.lower() in ['exit', 'quit']:
        print("Testing is complete. The program is closed.")
        break
        
    description_input = input("Input Game Description  : ")
    
    predicted_probs = predict_genre_probabilities(title_input, description_input)
    
    print("\nGenre Probability Analysis Results:")
    for item in predicted_probs:
        print(f" - {item['genre']}: {item['probability']:.2f}%")
    print("-" * 50 + "\n")