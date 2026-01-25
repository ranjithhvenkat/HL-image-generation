import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def list_available_models():
    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        print("Fetching available models...")
        
        # List models and filter for those that likely support generation
        for model in client.models.list():
            print(f"Model ID: {model.name}")
            # Optional: Print supported methods if available in the object
            # print(f"  - Details: {model}") 

    except Exception as e:
        print(f"Error fetching models: {e}")

if __name__ == "__main__":
    list_available_models()