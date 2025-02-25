import os
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_response(prompt):
    """
    Generate a response using Gemini's text generation model.
    
    Args:
        prompt (str): The prompt to send to the model
        
    Returns:
        str: The generated response
    """
    if not client:
        return "Error: Gemini client not initialized. Missing API key."
        
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm sorry, I encountered an error while generating a response."
