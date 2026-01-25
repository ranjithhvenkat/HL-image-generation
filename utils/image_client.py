import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
IMAGE_MODEL = os.getenv("IMAGE_MODEL_NAME", "gemini-3-pro-image-preview")

def generate_image(meta_prompt: str, reference_image_pil=None, aspect_ratio="1:1"):
    """
    Calls Nano Banana Pro (Gemini Image Model) to generate the final asset.
    """
    try:
        # Configuration for Image Generation
        # Note: If Nano Banana Pro supports 'image guidance' (ControlNet style),
        # we pass reference_image_pil. If it's pure Text-to-Image, we strictly use meta_prompt.
        
        # For this setup, we assume we are generating a NEW image based on the prompt.
        # If using standard Imagen 3 / Gemini Image logic:
        
        response = client.models.generate_images(
            model=IMAGE_MODEL,
            prompt=meta_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=aspect_ratio,
                # If the specific API supports referencing an input image for structure:
                # reference_image=reference_image_pil (Check specific API docs for parameter name)
            )
        )
        
        # The new SDK returns generated images usually as bytes or PIL objects
        if response.generated_images:
            # Return the first image
            return response.generated_images[0].image
        else:
            raise Exception("No image returned from API.")

    except Exception as e:
        print(f"Error in Nano Banana Pro: {e}")
        return None