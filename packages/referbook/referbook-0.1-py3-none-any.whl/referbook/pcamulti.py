# Task 14: Dimensionality reduction and visualization

from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

# Load dataset
newsgroups = fetch_20newsgroups(subset='all', remove=('headers', 'footers', 'quotes'))
data = newsgroups.data
labels = newsgroups.target
target_names = newsgroups.target_names

# TF-IDF vectorization
vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
X_tfidf = vectorizer.fit_transform(data)

# Reduce dimensionality
# Choose either PCA or t-SNE (uncomment the one you prefer)
reducer = PCA(n_components=2)  # PCA
# reducer = TSNE(n_components=2, perplexity=30, n_iter=1000)  # t-SNE (slower)

X_reduced = reducer.fit_transform(X_tfidf.toarray())

# Plotting
plt.figure(figsize=(12, 8))
scatter = plt.scatter(X_reduced[:, 0], X_reduced[:, 1], c=labels, cmap='tab20', alpha=0.6)
plt.title('Document Clusters using PCA/t-SNE')
plt.colorbar(scatter, label="Newsgroup Category")
plt.xlabel("Component 1")
plt.ylabel("Component 2")
plt.show()


"Multi-Class Text Classification with TF-IDF and KNN"

# Task 15: Multi-class text classification with KNN

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report

# Load dataset (update path as needed)
df = pd.read_csv("consumer_complaints.csv")

# Drop rows with missing complaints or categories
df = df[["Consumer complaint narrative", "Product"]].dropna()

# Features and labels
X = df["Consumer complaint narrative"]
y = df["Product"]

# TF-IDF
vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
X_tfidf = vectorizer.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

# KNN classifier
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)

# Evaluation
y_pred = knn.predict(X_test)
print(classification_report(y_test, y_pred))
