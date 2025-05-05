import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import LSTM, Embedding, Dense, Dropout, Bidirectional, CRF
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from nltk.tokenize import word_tokenize

# Sample data (word, tag)
data = [
    ("John", "B-PER"),
    ("Doe", "I-PER"),
    ("is", "O"),
    ("a", "O"),
    ("doctor", "O"),
    ("at", "O"),
    ("Stanford", "B-ORG"),
    ("University", "I-ORG")
]

# Convert to DataFrame for easy processing
df = pd.DataFrame(data, columns=["word", "tag"])

# Extract sentences and labels
sentences = []
tags = []
current_sentence = []
current_tags = []

for index, row in df.iterrows():
    current_sentence.append(row["word"])
    current_tags.append(row["tag"])
    
    # Assuming that a new sentence starts with a tag "O"
    if index == len(df) - 1 or df.iloc[index + 1]["tag"] == "O":
        sentences.append(current_sentence)
        tags.append(current_tags)
        current_sentence = []
        current_tags = []

# Create word and tag sets
words = list(set(df["word"]))
tags = list(set(df["tag"]))
n_words = len(words)
n_tags = len(tags)

# Encode tags and words
word2idx = {w: i + 1 for i, w in enumerate(words)}  # +1 for padding token
word2idx['PAD'] = 0
tag2idx = {t: i for i, t in enumerate(tags)}
idx2tag = {i: t for i, t in enumerate(tags)}

# Prepare data
X_data = [[word2idx[word] for word in sentence] for sentence in sentences]
y_data = [[tag2idx[tag] for tag in tag_sequence] for tag_sequence in tags]

# Pad sequences to have equal length
X_data = pad_sequences(X_data, padding='post')
y_data = pad_sequences(y_data, padding='post')

# Split into training and testing
X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, test_size=0.2, random_state=42)

# Model architecture
input = tf.keras.Input(shape=(X_train.shape[1],))
model = Embedding(input_dim=n_words + 1, output_dim=50, input_length=X_train.shape[1])(input)
model = Dropout(0.1)(model)
model = Bidirectional(LSTM(units=100, return_sequences=True, CRF=True))(model)
out = Dense(n_tags, activation="softmax")(model)

# Build and compile model
model = tf.keras.Model(input, out)
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

# Train the model
model.fit(X_train, np.expand_dims(y_train, -1), batch_size=32, epochs=5, validation_data=(X_test, np.expand_dims(y_test, -1)))

# Evaluation
y_pred = model.predict(X_test)
y_pred = np.argmax(y_pred, axis=-1)

# Example input sentence
input_sentence = ["John", "is", "a", "doctor", "at", "Stanford", "University"]

# Tokenize and predict NER tags
input_seq = [word2idx[word] if word in word2idx else word2idx["PAD"] for word in input_sentence]
input_seq = pad_sequences([input_seq], padding="post", maxlen=X_train.shape[1])

# Predict tags
predictions = model.predict(input_seq)
predicted_tags = np.argmax(predictions, axis=-1)

# Map predicted tags back to words
output = [(word, idx2tag[tag]) for word, tag in zip(input_sentence, predicted_tags[0])]

# Output
print("Input sentence:", input_sentence)
print("Predicted NER tags:", output)




"type 2 "

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import LSTM, Embedding, Dense, Dropout, Bidirectional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import os
import nltk

# 1. Load and preprocess CoNLL-2003 dataset
def load_conll2003_data(file_path):
    words = []
    tags = []
    sentence_words = []
    sentence_tags = []
    
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:  # Empty line indicates end of a sentence
                if sentence_words:
                    words.append(sentence_words)
                    tags.append(sentence_tags)
                    sentence_words = []
                    sentence_tags = []
            else:
                split_line = line.split()
                word, tag = split_line[0], split_line[-1]
                sentence_words.append(word)
                sentence_tags.append(tag)
    
    return words, tags

# Load training data
train_words, train_tags = load_conll2003_data("data/conll2003.train")
test_words, test_tags = load_conll2003_data("data/conll2003.test")

# 2. Prepare word and tag sets
all_words = [word for sentence in train_words for word in sentence]
all_tags = [tag for sentence in train_tags for tag in sentence]

words = list(set(all_words))
tags = list(set(all_tags))

n_words = len(words)
n_tags = len(tags)

# Create word and tag dictionaries
word2idx = {w: i + 1 for i, w in enumerate(words)}  # +1 for padding token
word2idx['PAD'] = 0
tag2idx = {t: i for i, t in enumerate(tags)}
idx2tag = {i: t for i, t in enumerate(tags)}

# 3. Prepare data
def encode_sentences(sentences, word2idx, tag2idx):
    X_data = [[word2idx[word] for word in sentence] for sentence in sentences]
    y_data = [[tag2idx[tag] for tag in tag_sequence] for tag_sequence in train_tags]
    return X_data, y_data

X_train, y_train = encode_sentences(train_words, word2idx, tag2idx)
X_test, y_test = encode_sentences(test_words, word2idx, tag2idx)

# 4. Pad sequences
X_train = pad_sequences(X_train, padding='post')
y_train = pad_sequences(y_train, padding='post')

X_test = pad_sequences(X_test, padding='post')
y_test = pad_sequences(y_test, padding='post')

# 5. Model architecture
input = tf.keras.Input(shape=(X_train.shape[1],))
model = Embedding(input_dim=n_words + 1, output_dim=50, input_length=X_train.shape[1])(input)
model = Dropout(0.1)(model)
model = Bidirectional(LSTM(units=100, return_sequences=True))(model)
out = Dense(n_tags, activation="softmax")(model)

# Build and compile model
model = tf.keras.Model(input, out)
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

# 6. Train the model
history = model.fit(X_train, np.expand_dims(y_train, -1), batch_size=32, epochs=5, validation_data=(X_test, np.expand_dims(y_test, -1)))

# 7. Evaluate the model
y_pred = model.predict(X_test)
y_pred = np.argmax(y_pred, axis=-1)

# Evaluate using classification report
print("Classification Report:")
print(classification_report(y_test.flatten(), y_pred.flatten(), target_names=tags))

# Compute confusion matrix
conf_matrix = confusion_matrix(y_test.flatten(), y_pred.flatten())

# 8. Visualization: Plot confusion matrix
plt.figure(figsize=(12, 8))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=tags, yticklabels=tags)
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.show()

# 9. Visualization: Plot accuracy and loss during training
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Accuracy Over Epochs')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Loss Over Epochs')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

plt.tight_layout()
plt.show()

# 10. Example input sentence (from CoNLL-2003 test set)
input_sentence = ["John", "Doe", "is", "a", "doctor", "at", "Stanford", "University"]

# Tokenize and predict NER tags
input_seq = [word2idx[word] if word in word2idx else word2idx["PAD"] for word in input_sentence]
input_seq = pad_sequences([input_seq], padding="post", maxlen=X_train.shape[1])

# Predict tags
predictions = model.predict(input_seq)
predicted_tags = np.argmax(predictions, axis=-1)

# Map predicted tags back to words
output = [(word, idx2tag[tag]) for word, tag in zip(input_sentence, predicted_tags[0])]

# Output
print("Input sentence:", input_sentence)
print("Predicted NER tags:", output)
