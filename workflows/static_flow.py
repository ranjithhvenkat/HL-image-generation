# workflows/static_flow.py
import streamlit as st
from utils import file_io, image_client

def execute(uploaded_files, product_specs, template_filename, **kwargs):
    """
    WORKFLOW 1: Static Prompting
    Reads a pre-written prompt from a file, appends user specs, and generates.
    """
    generated_images = []

    # 1. Read the Static Prompt (Template)
    # In this workflow, the template IS the prompt.
    base_prompt = file_io.load_template(template_filename)

    # 2. Combine with user specs (Simple Concatenation)
    final_prompt = f"{base_prompt}, {product_specs}"
    
    st.info(f"🚀 Running Static Workflow. Prompt: {final_prompt}")

    # 3. Iterate through images
    for img_file in uploaded_files:
        # Convert uploaded file to PIL
        pil_image = image_client.process_upload(img_file)
        
        # 4. Call Nano Banana Pro (Direct)
        result_image = image_client.generate_image(
            meta_prompt=final_prompt, 
            reference_image_pil=pil_image
        )
        
        generated_images.append(result_image)

    return generated_images