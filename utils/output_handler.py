import os
from datetime import datetime
from io import BytesIO

# Define where images go
OUTPUT_DIR = "outputs"

def save_image(pil_image, op_name, variant_name):
    """
    Saves the image locally and returns the file path.
    Structure: outputs/OpName/VariantName_Timestamp.png
    """
    # 1. Create base output folder if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 2. Create specific folder for this Operation (cleaner organization)
    # Replaces spaces with underscores for safe filenames
    safe_op_name = op_name.replace(" ", "_")
    safe_var_name = variant_name.replace(" ", "_")
    
    specific_dir = os.path.join(OUTPUT_DIR, safe_op_name)
    if not os.path.exists(specific_dir):
        os.makedirs(specific_dir)

    # 3. Generate Timestamped Filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_var_name}_{timestamp}.png"
    file_path = os.path.join(specific_dir, filename)

    # 4. Save to Disk
    pil_image.save(file_path, format="PNG")
    
    return file_path, filename

def convert_to_bytes(pil_image):
    """Converts PIL image to bytes for the Download Button"""
    buf = BytesIO()
    pil_image.save(buf, format="PNG")
    return buf.getvalue()