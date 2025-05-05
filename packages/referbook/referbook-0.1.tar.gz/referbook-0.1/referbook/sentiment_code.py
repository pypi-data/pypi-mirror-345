import pandas as pd
import numpy as np
import re
import nltk
import string

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, confusion_matrix

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download NLTK data (only once)
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

# -------------------------------
# 1. Load Dataset
# -------------------------------
# Example: Load your dataset here. Replace with the appropriate dataset path
df = pd.read_csv('your_dataset.csv')  # Replace with actual filename
df = df[['text_column_name', 'label_column_name']]  # Rename according to your dataset
df.columns = ['text', 'label']

# -------------------------------
# 2. Preprocess Text
# -------------------------------
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess(text):
    # Lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)
    # Remove punctuation and numbers
    text = re.sub(r"[^a-zA-Z\s]", '', text)
    # Tokenize
    tokens = nltk.word_tokenize(text)
    # Remove stopwords and lemmatize
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return " ".join(tokens)

df['text'] = df['text'].apply(preprocess)

# -------------------------------
# 3. Feature Extraction (Choose One)
# -------------------------------
# Bag-of-Words
# vectorizer = CountVectorizer()

# TF-IDF
vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(df['text'])
y = df['label']

# -------------------------------
# 4. Train-Test Split
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# -------------------------------
# 5. Model Training (Choose One)
# -------------------------------
# Naïve Bayes
model = MultinomialNB()

# SVM
# model = LinearSVC()

model.fit(X_train, y_train)

# -------------------------------
# 6. Evaluation
# -------------------------------
y_pred = model.predict(X_test)

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))































"""

combo

import pandas as pd
import re
import nltk
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, accuracy_score

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

# -------------------------------
# Load IMDb/Twitter Dataset
# -------------------------------
# Example: Replace with actual file and column names
df = pd.read_csv('your_dataset.csv')  # IMDb or Twitter subset
df = df[['text_column_name', 'label_column_name']]  # Update these
df.columns = ['text', 'label']

# -------------------------------
# Preprocessing Function
# -------------------------------
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    tokens = nltk.word_tokenize(text)
    tokens = [lemmatizer.lemmatize(w) for w in tokens if w not in stop_words]
    return " ".join(tokens)

df['text'] = df['text'].apply(preprocess)

# -------------------------------
# Define Vectorizers and Models
# -------------------------------
vectorizers = {
    'BoW': CountVectorizer(),
    'TF-IDF': TfidfVectorizer()
}

models = {
    'Naive Bayes': MultinomialNB(),
    'SVM': LinearSVC()
}

# -------------------------------
# Train and Evaluate Each Combo
# -------------------------------
for vect_name, vect in vectorizers.items():
    X = vect.fit_transform(df['text'])
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    for model_name, model in models.items():
        print(f"\n=== {vect_name} + {model_name} ===")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        print("Accuracy:", accuracy_score(y_test, y_pred))
        print(classification_report(y_test, y_pred))




"""