import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

load_dotenv()

# Initialize Client
# We explicitly set the version to 'v1alpha' because 'preview' models 
# usually live there, not in the stable v1.
client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
    http_options={'api_version': 'v1alpha',
    #'timeout': 800 
    }
)

#IMAGE_MODEL = os.getenv("IMAGE_MODEL_NAME", "nano-banana-pro-preview")
IMAGE_MODEL = os.getenv("IMAGE_MODEL_NAME", "gemini-3-pro-image-preview") 
#IMAGE_MODEL = os.getenv("IMAGE_MODEL_NAME", "imagen-4.0-generate-001") 

def generate_image(meta_prompt: str, reference_image_pil=None):
    """
    Calls the Nano Banana Pro / Gemini 3 model to generate an image.
    Uses 'generate_content' with response_modalities=['IMAGE'].
    """
    try:
        print(f"🎨 Nano Banana Pro: Generating with model '{IMAGE_MODEL}'...")

        # 1. Prepare Content
        # Gemini 3 supports interleaving Text and Images.
        contents = []
        
        # If we have a reference image (e.g. for Fabric change), add it first
        if reference_image_pil:
            contents.append(reference_image_pil)
            
        # Add the Prompt
        contents.append(meta_prompt)

        # 2. Configure for IMAGE Output
        # This tells the model: "Don't chat with me, just make an image."
        config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            temperature=0.9, # Higher creativity for seasonal themes
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_ONLY_HIGH"
                )
            ]
        )

        # 3. Call the API
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=contents,
            config=config
        )

        # 4. Extract Image
        # Iterate through parts to find the image binary
        if response.parts:
            for part in response.parts:
                # Check for executable code or direct image bytes
                if part.inline_data:
                    return Image.open(BytesIO(part.inline_data.data))
                
                # Check for newer SDK object attribute
                if hasattr(part, 'image'):
                    # Some versions return a PIL image directly here
                    return part.image

        # If we get text instead of an image (e.g., "I cannot generate that")
        if response.text:
            print(f"⚠️ API Refusal: {response.text}")
            raise Exception(f"Model refused to generate image: {response.text}")

        return None

    except Exception as e:
        print(f"❌ Error in Image Client: {e}")
        raise e

def process_upload(uploaded_file):
    """Converts Streamlit UploadedFile -> PIL Image."""
    if uploaded_file is None:
        return None
    return Image.open(uploaded_file)