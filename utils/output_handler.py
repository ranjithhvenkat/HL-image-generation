import os
from datetime import datetime
from PIL import Image
from io import BytesIO


# Base output directory
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")


def _ensure_dir(path: str):
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def save_image(pil_image: Image.Image, operation_name: str, variant_name: str = "") -> tuple:
    """
    Saves a generated image locally in a clean folder structure.

    Structure:
        outputs/
        ├── Fabric_Color_Simulation/
        │   ├── Blue_Velvet_20250713_143022.png
        │   └── Red_Silk_20250713_143055.png
        ├── Seasonal_Thematic_Contexts/
        │   ├── Christmas_20250713_144012.png
        │   └── Cyberpunk_20250713_144030.png
        └── SKU/
            └── Front_View_20250713_145001.png

    Args:
        pil_image: The PIL image to save.
        operation_name: Name of the operation (used as folder name).
        variant_name: Sanitized user spec snippet (used in filename).

    Returns:
        tuple: (full_save_path, filename)
    """
    # Create operation-specific folder
    operation_dir = os.path.join(OUTPUT_DIR, operation_name)
    _ensure_dir(operation_dir)

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Build filename
    if variant_name:
        filename = f"{variant_name}_{timestamp}.png"
    else:
        filename = f"output_{timestamp}.png"

    # Full path
    save_path = os.path.join(operation_dir, filename)

    # Save
    pil_image.save(save_path, format="PNG", quality=100)
    print(f"💾 Saved: {save_path}")

    return save_path, filename


def convert_to_bytes(pil_image: Image.Image, format: str = "PNG") -> bytes:
    """
    Converts PIL Image to bytes for Streamlit download button.
    """
    buffered = BytesIO()
    pil_image.save(buffered, format=format)
    return buffered.getvalue()


def get_operation_outputs(operation_name: str) -> list:
    """
    Returns list of all saved images for a given operation.
    Useful for browsing past generations.
    """
    operation_dir = os.path.join(OUTPUT_DIR, operation_name)
    if not os.path.exists(operation_dir):
        return []

    files = []
    for f in sorted(os.listdir(operation_dir), reverse=True):
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            files.append({
                "filename": f,
                "path": os.path.join(operation_dir, f),
            })
    return files