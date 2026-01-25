import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Initialize Client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-2.5-flash")

def generate_meta_prompt(product_specs: str, template_text: str, user_image_pil=None) -> str:
    """
    Uses Gemini 2.5 Flash to generate a detailed image description.
    
    Args:
        product_specs: User's text description.
        template_text: The system instruction from the .txt file.
        user_image_pil: (Optional) The PIL image if the prompt needs visual context.
    """
    try:
        inputs = []
        
        # 1. Add System/Template Instruction
        inputs.append(template_text)
        
        # 2. Add the Image (if provided, multimodal reasoning)
        if user_image_pil:
            inputs.append(user_image_pil)
            
        # 3. Add User Specs
        inputs.append(f"\n\nProduct Specifications provided by user: {product_specs}")
        
        # 4. Config for precise instruction following
        config = types.GenerateContentConfig(
            temperature=0.7, # Creativity balance
            top_p=0.95,
            top_k=40
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=inputs,
            config=config
        )
        
        return response.text.strip()

    except Exception as e:
        return f"Error generating meta-prompt: {str(e)}"