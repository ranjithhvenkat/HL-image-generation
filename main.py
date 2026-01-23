#version 1 of main.py.
#Simple set up using streamlit to mimic the frontend of user
import streamlit as st
import yaml
import os
from typing import List, Dict, Any

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
            help="Describe the product exactly as it appears. This helps the AI preserve product identity."
        )

    # ------------------------------------------------
    # SECTION 4: EXECUTION
    # ------------------------------------------------
    st.markdown("---")
    
    # State validation
    ready_to_run = uploaded_files or product_specs and current_op
    
    if st.button("Generate Output", type="primary", disabled=not ready_to_run):
        
        # UI Feedback
        st.status("Processing...", expanded=True)
        
        # ---------------------------------------------
        # PLACEHOLDER FOR UTILITY CONNECTION
        # ---------------------------------------------
        st.write(f"**Selected Operation:** {current_op['name']}")
        if current_variant:
            st.write(f"**Selected Variant:** {current_variant['name']}")
            st.write(f"**Template File:** {current_variant['template']}")
        
        st.write(f"**Images Queued:** {len(uploaded_files)}")
        st.write(f"**Workflow Engine:** {current_op['workflow']}")
        
        # In the next step, we will import utils here and pass these variables:
        # utils.execute_workflow(current_op['workflow'], uploaded_files, product_specs, current_variant['template'])

if __name__ == "__main__":
    main()