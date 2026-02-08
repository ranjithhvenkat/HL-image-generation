import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# Load environment variables
load_dotenv()

def test_imagen_generation():
    # 1. Initialize Client
    # Note: We do not strictly need 'v1alpha' for Imagen 4 usually, 
    # but we keep it consistent if your key is in preview.
    client = genai.Client(
        api_key=os.getenv("GOOGLE_API_KEY"),
        http_options={'api_version': 'v1alpha'} 
    )

    model_id = 'imagen-4.0-generate-001'
    
    print(f"🎨 Testing Imagen Generation with: {model_id}")

    try:
        # 2. Call the Generate Images Endpoint
        # CRITICAL: This is .generate_images(), NOT .generate_content()
        response = client.models.generate_images(
            model=model_id,
            prompt='A futuristic robot holding a red skateboard, 8k resolution, cinematic lighting',
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",
                # safety_filter_level="block_only_high" # Optional
            )
        )

        # 3. Handle Response
        if response.generated_images:
            for idx, generated_image in enumerate(response.generated_images):
                print(f"✅ Image {idx+1} Generated Successfully!")
                
                # Retrieve the image object
                img = generated_image.image
                
                # Show it (opens in default viewer)
                img.show()
                
                # Save it locally to verify
                filename = f"test_imagen_result_{idx}.png"
                img.save(filename)
                print(f"💾 Saved to {filename}")
        else:
            print("⚠️ No images returned.")

    except Exception as e:
        print(f"❌ Error during generation: {e}")

if __name__ == "__main__":
    test_imagen_generation()