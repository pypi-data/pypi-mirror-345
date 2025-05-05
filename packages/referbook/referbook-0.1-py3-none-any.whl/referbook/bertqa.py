import torch
from transformers import BertTokenizer, BertForQuestionAnswering
from transformers import pipeline

# Load the pre-trained BERT model and tokenizer from Hugging Face's transformers library
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

# Using Hugging Face's pipeline for Question Answering
qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

# Define a function to answer questions
def answer_question(context, question):
    # Use the QA pipeline to get the answer from the context
    result = qa_pipeline({'context': context, 'question': question})
    return result['answer']

# Example context (document or paragraph)
context = """
BERT (Bidirectional Encoder Representations from Transformers) is a transformer-based model designed to understand the context of a word in search queries.
It is one of the most powerful models for Natural Language Processing (NLP) and has significantly improved performance on tasks like question answering, sentiment analysis, and text classification.
BERT is pre-trained on a large corpus of text and can be fine-tuned for specific tasks.
"""

# Example question
question = "What is BERT?"

# Get the answer
answer = answer_question(context, question)

print(f"Question: {question}")
print(f"Answer: {answer}")
