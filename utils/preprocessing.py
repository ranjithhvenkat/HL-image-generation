import base64
from PIL import Image
from io import BytesIO

def process_upload(uploaded_file):
    """
    Converts Streamlit UploadedFile -> PIL Image.
    Used for resizing or displaying in the UI before sending to API.
    """
    if uploaded_file is None:
        return None
    return Image.open(uploaded_file)

def image_to_bytes(pil_image, format="PNG"):
    """
    Converts PIL Image -> Bytes. 
    Required for passing images to the Google GenAI SDK.
    """
    buffered = BytesIO()
    pil_image.save(buffered, format=format)
    return buffered.getvalue()

def encode_image_base64(pil_image):
    """
    Helper if we ever need raw JSON payloads.
    """
    buffered = BytesIO()
    pil_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")