import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Sample documents
doc1 = """
Machine learning is a branch of artificial intelligence (AI) that focuses on building applications that learn from data and improve over time.
It is used in a variety of fields, including healthcare, finance, and marketing.
"""
doc2 = """
Artificial intelligence, or AI, refers to the simulation of human intelligence in machines that are programmed to think like humans and mimic their actions.
Machine learning is a subset of AI that enables machines to learn from data and improve without explicit programming.
"""

# Preprocessing function
def preprocess(text):
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    text = ' '.join([word for word in text.split() if word not in stop_words])
    # Stem the words
    stemmer = PorterStemmer()
    text = ' '.join([stemmer.stem(word) for word in text.split()])
    return text

# Preprocess documents
doc1_cleaned = preprocess(doc1)
doc2_cleaned = preprocess(doc2)

# Compute TF-IDF and Cosine Similarity
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform([doc1_cleaned, doc2_cleaned])
cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

print(f"Cosine Similarity after preprocessing: {cosine_sim[0][0]:.4f}")
