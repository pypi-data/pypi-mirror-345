import torch
from transformers import BertTokenizer, BertModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load pre-trained BERT model and tokenizer from Hugging Face
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased')

# Use sentence-transformers to get embeddings for sentences
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to encode the document into sentences
def split_into_sentences(text):
    # Basic sentence splitting (could be replaced with a better tokenizer)
    sentences = text.split('. ')
    return [sentence.strip() for sentence in sentences if sentence]

# Function to get BERT embeddings for sentences
def get_bert_embeddings(sentences):
    embeddings = []
    for sentence in sentences:
        inputs = tokenizer(sentence, return_tensors='pt', truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = bert_model(**inputs)
        embeddings.append(outputs.last_hidden_state.mean(dim=1).squeeze().numpy())
    return np.array(embeddings)

# Function to get sentence embeddings using Sentence-Transformers
def get_sentence_embeddings(sentences):
    embeddings = sentence_model.encode(sentences)
    return np.array(embeddings)

# Function to rank sentences based on cosine similarity
def rank_sentences(text, sentences):
    # Get embeddings for the entire text (document embedding)
    doc_embedding = sentence_model.encode([text])[0]
    
    # Get sentence embeddings
    sentence_embeddings = get_sentence_embeddings(sentences)
    
    # Calculate cosine similarities between document and each sentence
    cosine_similarities = cosine_similarity([doc_embedding], sentence_embeddings)
    
    # Get sentences ranked by cosine similarity
    ranked_sentences = [(sentences[i], cosine_similarities[0][i]) for i in range(len(sentences))]
    ranked_sentences.sort(key=lambda x: x[1], reverse=True)
    
    return ranked_sentences

# Function to generate the extractive summary
def extractive_summary(text, n=3):
    sentences = split_into_sentences(text)
    ranked_sentences = rank_sentences(text, sentences)
    
    # Extract top N sentences
    top_n_sentences = [ranked_sentences[i][0] for i in range(n)]
    
    return ' '.join(top_n_sentences)

# Example input text
input_text = """
Machine learning is a branch of artificial intelligence (AI) that focuses on building applications that learn from data and improve over time.
It is used in a variety of fields, including healthcare, finance, and marketing.
Natural language processing (NLP) is a subset of AI focused on enabling machines to understand and generate human language.
The field of machine learning has gained significant attention and investment over the last decade due to the availability of big data and improved computational power.
Applications of machine learning include speech recognition, image processing, and recommendation systems.
"""

# Generate the summary
summary = extractive_summary(input_text, n=3)
print("Extractive Summary:")
print(summary)
