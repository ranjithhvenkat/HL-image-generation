#version 1 of main.py.
#Simple set up using streamlit to mimic the frontend of user
import streamlit as st
import yaml
import os
from typing import List, Dict, Any
from workflows import static_flow, dynamic_flow
from utils import output_handler 
# ==========================================
# WORKFLOW REGISTRY
# ==========================================
# This dictionary maps the YAML 'workflow' string to the Python module
WORKFLOW_MAP = {
    "static_prompting": static_flow,
    "dynamic_prompting": dynamic_flow,
    # Future scalability:
    # "masking_workflow": masking_flow 
}
# ==========================================
# CONFIGURATION & SETUP
# ==========================================
CONFIG_PATH = os.path.join("config", "operations.yaml")

def load_config() -> List[Dict[str, Any]]:
    """
    Loads the operations configuration from the YAML file.
    Returns a list of operation dictionaries.
    """
    if not os.path.exists(CONFIG_PATH):
        st.error(f"Configuration file not found at: {CONFIG_PATH}")
        return []
    
    with open(CONFIG_PATH, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data.get('operations', [])
        except yaml.YAMLError as exc:
            st.error(f"Error parsing YAML file: {exc}")
            return []

# ==========================================
# UI HELPER FUNCTIONS
# ==========================================
def format_op_display(op: Dict) -> str:
    """Formats the operation for the dropdown display."""
    # We display Name and Description, hiding the ID from the immediate view
    # strictly mimicking a user-friendly frontend
    return f"{op['name']} | {op['description']}"

def format_variant_display(variant: Dict) -> str:
    """Formats the variant for the dropdown display."""
    return f"{variant['name']} - {variant['description']}"

# ==========================================
# MAIN APPLICATION
# ==========================================
def main():
    st.set_page_config(page_title="Nano Banana Pro - GenAI Studio", layout="wide")
    
    st.title("Version 1 streamlit dashboard")
    st.markdown("---")

    # 1. Load Operations
    operations = load_config()
    
    if not operations:
        st.warning("No operations found. Please check config/operations.yaml")
        return

    # Container for the Control Panel
    with st.container():
        col1, col2 = st.columns([1, 1])

        # ------------------------------------------------
        # SECTION 1: OPERATION SELECTION
        # ------------------------------------------------
        with col1:
            st.subheader("1. Select Strategy")
            
            # Select Operation
            # We map the display string back to the actual operation object
            selected_op_index = st.selectbox(
                "Choose Operation",
                range(len(operations)),
                format_func=lambda i: format_op_display(operations[i]),
                help="Select the high-level modification goal."
            )
            
            current_op = operations[selected_op_index]
            
            # Debug/Dev info (Optional, can be removed for pure UI feel)
            st.caption(f"System ID: {current_op['id']} | Workflow: {current_op['workflow']}")

        # ------------------------------------------------
        # SECTION 2: VARIANT SELECTION
        # ------------------------------------------------
        with col2:
            st.subheader("2. Select Variant")
            
            variants = current_op.get('variants', [])
            
            if variants:
                selected_variant_index = st.selectbox(
                    "Choose Variant",
                    range(len(variants)),
                    format_func=lambda i: format_variant_display(variants[i]),
                    help="Select the specific style or theme."
                )
                current_variant = variants[selected_variant_index]
            else:
                st.info("No specific variants defined for this operation. Using default.")
                current_variant = None

    st.markdown("---")

    # ------------------------------------------------
    # SECTION 3: ASSET UPLOAD & SPECS
    # ------------------------------------------------
    st.subheader("3. Add Assets")
    
    c1, c2 = st.columns([1, 2])
    
    with c1:
        # Multiple Image Upload Support
        uploaded_files = st.file_uploader(
            "Upload Reference Images", 
            type=['png', 'jpg', 'jpeg', 'webp'], 
            accept_multiple_files=True
        )
        
    with c2:
        # Product Context (Crucial for the LLM Meta-Prompt)
        product_specs = st.text_area(
            "Product Specifications / Context",
            placeholder="E.g., A red leather modern sofa, 3-seater...",
            height=100,
            help="provide required product specs or requiremets here."
        )

    # ------------------------------------------------
    # SECTION 4: EXECUTION
    # ------------------------------------------------
    st.markdown("---")
    if st.button("Generate Output", type="primary"):
        
        # 1. Identify the requested workflow string (e.g., "dynamic_prompting")
        workflow_name = current_op.get('workflow')
        
        # 2. Get the corresponding Python module
        workflow_module = WORKFLOW_MAP.get(workflow_name)
        
        if not workflow_module:
            st.error(f"Workflow '{workflow_name}' is not defined in main.py registry.")
            return

        # 3. Execute the Workflow
        try:
            results = workflow_module.execute(
                uploaded_files=uploaded_files,
                product_specs=product_specs,
                template_filename=current_variant['template']
            )
            
            # 4. Display & Save Results
            st.success("Generation Complete!")
            
            # Create columns if multiple images
            cols = st.columns(len(results))
            
            for idx, img in enumerate(results):
                with cols[idx]:
                    # A. Display Image
                    st.image(img, caption=f"Result {idx+1}", use_container_width=True)
                    
                    # B. Save to Disk (Auto-save)
                    save_path, filename = output_handler.save_image(
                        img, 
                        current_op['name'], 
                        current_variant['name']
                    )
                    st.caption(f"Saved locally to: `{save_path}`")
                    
                    # C. Download Button
                    btn = st.download_button(
                        label="⬇️ Download Image",
                        data=output_handler.convert_to_bytes(img),
                        file_name=filename,
                        mime="image/png"
                    )
                
        except Exception as e:
            st.error(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    main()