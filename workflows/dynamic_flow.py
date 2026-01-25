# workflows/dynamic_flow.py
import streamlit as st
from utils import file_io, llm_client, image_client, preprocessing

def execute(uploaded_files, product_specs, template_filename, **kwargs):
    """
    WORKFLOW 2: Dynamic Prompting
    Uses Gemini Flash (LLM) to write a detailed Meta-Prompt, then generates.
    """
    generated_images = []

    # 1. Load the System Instruction (The "How-To" for the LLM)
    system_template = file_io.load_template(template_filename)

    for img_file in uploaded_files:
        # Process image for API
        pil_image = preprocessing.process_upload(img_file)
        
        # 2. LLM Step: Create the Meta-Prompt
        # We pass the image to the LLM so it can "see" what it's modifying
        with st.status("🤖 AI Planner is thinking...", expanded=True):
            meta_prompt = llm_client.generate_meta_prompt(
                product_specs=product_specs, 
                template_text=system_template, 
                user_image_pil=pil_image
            )
            st.write(f"**Generated Prompt:** {meta_prompt}")

        # 3. Image Gen Step: Call Nano Banana Pro
        with st.status("🎨 Nano Banana Pro is creating...", expanded=True):
            result_image = image_client.generate_image(
                meta_prompt=meta_prompt, 
                reference_image_pil=pil_image
            )
        
        generated_images.append(result_image)

    return generated_images