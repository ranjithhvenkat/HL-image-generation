import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

load_dotenv()

# Initialize Client
client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
    http_options={'api_version': 'v1alpha'}
)

IMAGE_MODEL = os.getenv("IMAGE_MODEL_NAME", "gemini-3-pro-image-preview")

# Aspect ratio to pixel dimensions mapping
ASPECT_RATIO_DIMENSIONS = {
    "1:1": (1024, 1024),
    "16:9": (1536, 864),
    "9:16": (864, 1536),
    "4:3": (1344, 1008),
    "3:4": (1008, 1344),
}


def generate_image(meta_prompt: str, reference_images_pil=None, aspect_ratio: str = "1:1"):
    """
    Calls Nano Banana Pro / Gemini 3 to generate an image.

    Args:
        meta_prompt: The generated prompt from LLM.
        reference_images_pil: List of PIL reference images.
        aspect_ratio: Output aspect ratio (e.g., '1:1', '16:9', '9:16').
    """
    try:
        print(f"🎨 Nano Banana Pro: Generating with model '{IMAGE_MODEL}'...")
        print(f"📐 Aspect Ratio: {aspect_ratio}")

        # 1. Get target dimensions
        width, height = ASPECT_RATIO_DIMENSIONS.get(aspect_ratio, (1024, 1024))
        print(f"📏 Target Dimensions: {width}x{height}")

        # 2. Prepare Content — ALL reference images first, then prompt
        contents = []

        if reference_images_pil:
            for idx, img in enumerate(reference_images_pil):
                contents.append(f"[Reference Image {idx + 1}]:")
                contents.append(img)

        # Append aspect ratio instruction to the prompt
        prompt_with_ratio = (
            f"{meta_prompt}\n\n"
            f"[OUTPUT SPECIFICATION: Generate this image in {aspect_ratio} aspect ratio, "
            f"targeting {width}x{height} pixel dimensions.]"
        )
        contents.append(prompt_with_ratio)

        # 3. Configure for IMAGE Output
        config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            temperature=0.9,
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_ONLY_HIGH"
                )
            ]
        )

        # 4. Call the API
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=contents,
            config=config
        )

        # 5. Extract Image
        if response.parts:
            for part in response.parts:
                if part.inline_data:
                    img = Image.open(BytesIO(part.inline_data.data))
                    # Resize to target dimensions if needed
                    if img.size != (width, height):
                        img = img.resize((width, height), Image.LANCZOS)
                        print(f"📐 Resized to {width}x{height}")
                    return img
                if hasattr(part, 'image'):
                    return part.image

        if response.text:
            print(f"⚠️ API Refusal: {response.text}")
            raise Exception(f"Model refused to generate image: {response.text}")

        return None

    except Exception as e:
        print(f"❌ Error in Image Client: {e}")
        raise e