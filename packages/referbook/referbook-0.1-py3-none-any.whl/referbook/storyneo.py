from transformers import GPTNeoForCausalLM, GPT2Tokenizer
import torch

# Load pre-trained GPT-Neo model and tokenizer from Hugging Face
model_name = "EleutherAI/gpt-neo-2.7B"  # You can use smaller models like 'gpt-neo-125M' for faster results
model = GPTNeoForCausalLM.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# Set the model to evaluation mode
model.eval()

# Define the storytelling function
def generate_story(prompt, max_length=200, temperature=0.7):
    # Encode the input prompt into tokens
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    
    # Generate text using GPT-Neo
    outputs = model.generate(
        inputs,
        max_length=max_length,
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        temperature=temperature,
        top_p=0.95,
        top_k=50,
        do_sample=True,
        early_stopping=True
    )
    
    # Decode the generated text into a human-readable string
    story = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return story

# Example prompt to start storytelling
prompt = """
In a faraway kingdom, there was a young prince named Orion. He had everything a prince could wish for: wealth, power, and land.
But despite all his riches, Orion was deeply lonely. One day, he set off on an adventure to find something that had been missing in his life...
"""

# Generate a story based on the prompt
story = generate_story(prompt)
print("Generated Story:")
print(story)
