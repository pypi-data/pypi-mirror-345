import random
from transformers import pipeline
import nltk
from nltk.chat.util import Chat, reflections

# Download NLTK data for basic chatbots
nltk.download('punkt')

# Step 3: Define the individual agents

class GeneralQueryAgent:
    def __init__(self):
        self.name = "General Query Agent"
        self.chatbot = pipeline("conversational", model="microsoft/DialoGPT-medium")
    
    def respond(self, user_query):
        # The agent uses a conversational model to respond to queries.
        return self.chatbot(user_query)[0]['generated_text']

class OrderStatusAgent:
    def __init__(self):
        self.name = "Order Status Agent"
    
    def respond(self, user_query):
        # Simulate order status check.
        order_status = ["Order is on the way!", "Order has been delivered!", "Order is delayed due to weather conditions."]
        return random.choice(order_status)

class ReturnProcessingAgent:
    def __init__(self):
        self.name = "Return Processing Agent"
    
    def respond(self, user_query):
        # Simulate return processing.
        return "Your return request has been successfully processed. You'll receive a confirmation email shortly."

# Step 4: Create a main agent to handle the delegation

class CustomerSupportAgent:
    def __init__(self):
        self.general_query_agent = GeneralQueryAgent()
        self.order_status_agent = OrderStatusAgent()
        self.return_processing_agent = ReturnProcessingAgent()
    
    def route_query(self, user_query):
        # Determine which agent is needed for the query
        if "order" in user_query.lower() and "status" in user_query.lower():
            return self.order_status_agent.respond(user_query)
        elif "return" in user_query.lower():
            return self.return_processing_agent.respond(user_query)
        else:
            return self.general_query_agent.respond(user_query)

# Step 5: Build the Dialogue Management System

def chatbot_conversation():
    support_agent = CustomerSupportAgent()
    print("Welcome to our customer support system! How can I assist you today?")
    
    while True:
        user_query = input("You: ")
        if user_query.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye! Have a great day.")
            break
        response = support_agent.route_query(user_query)
        print(f"Support Agent: {response}")

# Step 6: Test the System
if __name__ == "__main__":
    chatbot_conversation()
