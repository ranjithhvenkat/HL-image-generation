import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Initialize Client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-2.5-flash")


def generate_meta_prompt(
    user_specs: str,
    template_text: str,
    user_images_pil=None  # ✅ Changed: accepts LIST of images
) -> str:
    """
    Uses Gemini 2.5 Flash to generate a detailed image generation prompt.

    Args:
        user_specs: Combined product specifications and user requirements.
        template_text: The system instruction template for this operation.
        user_images_pil: (Optional) List of PIL images for visual context.
    """
    try:
        inputs = []

        # 1. System/Template Instruction (sets the operational context)
        inputs.append(template_text)

        # 2. ALL Reference Images (multimodal reasoning)
        if user_images_pil:
            for idx, img in enumerate(user_images_pil):
                inputs.append(f"\n[Reference Image {idx + 1}]:")
                inputs.append(img)

        # 3. User Specifications & Requirements
        inputs.append(
            f"\n\n**User Specifications & Requirements:**\n"
            f"{user_specs}"
        )

        # 4. Config
        config = types.GenerateContentConfig(
            temperature=0.7,
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