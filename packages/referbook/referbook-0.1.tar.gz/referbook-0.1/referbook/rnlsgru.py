import os
import numpy as np
import librosa
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, GRU, SimpleRNN, Flatten
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt  # Import matplotlib

# Load audio files from the Free Spoken Digit Dataset (FSDD)
DATA_PATH = 'recordings/'  # Download from: https://github.com/Jakobovski/free-spoken-digit-dataset

def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=None)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return np.mean(mfccs.T, axis=0)

X, y = [], []
for filename in os.listdir(DATA_PATH):
    if filename.endswith('.wav'):
        label = int(filename[0])  # Digit label
        y.append(label)
        features = extract_features(os.path.join(DATA_PATH, filename))
        X.append(features)

X = np.array(X)
y = to_categorical(np.array(y), num_classes=10)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_train = X_train[..., np.newaxis]
X_test = X_test[..., np.newaxis]

def build_model(cell_type='LSTM'):
    model = Sequential()
    if cell_type == 'RNN':
        model.add(SimpleRNN(64, input_shape=(X_train.shape[1], 1)))
    elif cell_type == 'GRU':
        model.add(GRU(64, input_shape=(X_train.shape[1], 1)))
    else:
        model.add(LSTM(64, input_shape=(X_train.shape[1], 1)))
    model.add(Dense(10, activation='softmax'))
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

results = {}
for model_type in ['RNN', 'GRU', 'LSTM']:
    print(f"\nTraining {model_type} model:")
    model = build_model(model_type)
    model.fit(X_train, y_train, epochs=10, batch_size=16, validation_data=(X_test, y_test), verbose=0)
    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    results[model_type] = acc
    print(f"{model_type} Accuracy: {acc:.4f}")

# Print final comparison
print("\nFinal Accuracy Comparison:")
for model_type, acc in results.items():
    print(f"{model_type}: {acc:.4f}")

# Plot comparison using matplotlib
model_types = list(results.keys())
accuracies = list(results.values())

plt.figure(figsize=(8, 6))
plt.bar(model_types, accuracies, color=['blue', 'green', 'red'])
plt.xlabel('Model Type')
plt.ylabel('Accuracy')
plt.title('Comparison of Model Accuracy')
plt.ylim([0, 1])  # Set y-axis limits from 0 to 1 for accuracy
plt.show()



"tfidf vector"


from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Load the 20 Newsgroups dataset
newsgroups = fetch_20newsgroups(subset='all')
X, y = newsgroups.data, newsgroups.target

# TF-IDF Vectorization
vectorizer = TfidfVectorizer(stop_words='english', max_features=10000)
X_tfidf = vectorizer.fit_transform(X)

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

# Train the Naive Bayes Classifier
clf = MultinomialNB()
clf.fit(X_train, y_train)

# Predict and evaluate the model on the test set
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred, target_names=newsgroups.target_names))

# Now, let's classify some custom input text (new articles)
custom_texts = [
    "The government of the United States is considering new policies on climate change and energy production.",
    "In the world of technology, there are continuous advancements in the field of artificial intelligence and machine learning.",
    "The upcoming baseball season will feature new teams, coaches, and exciting game strategies for fans."
]

# Transform custom texts into TF-IDF features using the trained vectorizer
X_custom_tfidf = vectorizer.transform(custom_texts)

# Predict the categories for the custom texts
custom_preds = clf.predict(X_custom_tfidf)

# Output the predicted categories for the custom texts
for i, text in enumerate(custom_texts):
    print(f"\nText {i+1}: {text}")
    print(f"Predicted Category: {newsgroups.target_names[custom_preds[i]]}")



"performance in news "


from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import classification_report

# Load the 20 Newsgroups dataset
newsgroups = fetch_20newsgroups(subset='all')
X, y = newsgroups.data, newsgroups.target

# TF-IDF Vectorization
vectorizer = TfidfVectorizer(stop_words='english', max_features=10000)
X_tfidf = vectorizer.fit_transform(X)

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

# KNN Accuracy for different K values
accuracies = []
k_values = list(range(1, 21))

for k in k_values:
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, y_train)
    acc = knn.score(X_test, y_test)
    accuracies.append(acc)
    print(f"K={k}, Accuracy={acc:.4f}")

# Plotting KNN Accuracy for different K values
plt.figure(figsize=(10, 6))
plt.plot(k_values, accuracies, marker='o')
plt.title("KNN Accuracy for different K values")
plt.xlabel("K")
plt.ylabel("Accuracy")
plt.grid(True)
plt.show()

# Let's predict with K=5 (for example) and print classification report for evaluation
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)
y_pred = knn.predict(X_test)

print("\nClassification Report for K=5:")
print(classification_report(y_test, y_pred, target_names=newsgroups.target_names))

# Now, let's classify some custom input text (new articles)
custom_texts = [
    "The government of the United States is considering new policies on climate change and energy production.",
    "In the world of technology, there are continuous advancements in the field of artificial intelligence and machine learning.",
    "The upcoming baseball season will feature new teams, coaches, and exciting game strategies for fans."
]

# Transform custom texts into TF-IDF features using the trained vectorizer
X_custom_tfidf = vectorizer.transform(custom_texts)

# Predict the categories for the custom texts
custom_preds = knn.predict(X_custom_tfidf)

# Output the predicted categories for the custom texts
for i, text in enumerate(custom_texts):
    print(f"\nText {i+1}: {text}")
    print(f"Predicted Category: {newsgroups.target_names[custom_preds[i]]}")
