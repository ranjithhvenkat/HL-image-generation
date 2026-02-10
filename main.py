import streamlit as st
import yaml
import os
import re
from typing import List, Dict, Any
from workflows import static_flow, dynamic_flow
from utils import output_handler
from PIL import Image 
# ==========================================
# WORKFLOW REGISTRY
# ==========================================
WORKFLOW_MAP = {
    "static_prompting": static_flow,
    "dynamic_prompting": dynamic_flow,
}

# ==========================================
# ASPECT RATIO OPTIONS
# ==========================================
ASPECT_RATIOS = {
    "1:1 (Square)": "1:1",
    "16:9 (Landscape)": "16:9",
    "9:16 (Portrait)": "9:16",
    "4:3 (Standard)": "4:3",
    "3:4 (Portrait Standard)": "3:4",
}

# ==========================================
# CONFIGURATION & SETUP
# ==========================================
CONFIG_PATH = os.path.join("config", "operations.yaml")


def load_config() -> List[Dict[str, Any]]:
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


def sanitize_filename(text: str) -> str:
    """Helper to turn 'Make it Christmas!!' into 'Make_it_Christmas'"""
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return clean.strip().replace(' ', '_')[:20]


# ==========================================
# MAIN APPLICATION
# ==========================================
def main():
    st.set_page_config(page_title="Nano Banana Pro", layout="wide")

    st.title("🍌 Nano Banana Pro: GenAI Studio")
    st.markdown("---")

    operations = load_config()
    if not operations:
        return

    # ------------------------------------------------
    # INPUT 1: Operation Selection
    # ------------------------------------------------
    st.subheader("1. Select Operation")
    selected_op_index = st.selectbox(
        "Choose Operation",
        range(len(operations)),
        format_func=lambda i: f"[{operations[i]['id']}] {operations[i]['name']} — {operations[i]['description']}"
    )
    current_op = operations[selected_op_index]

    st.markdown("---")

    # ------------------------------------------------
    # INPUT 2: User Specifications
    # ------------------------------------------------
    st.subheader("2. Product Specifications & Requirements")
    user_specs = st.text_area(
        "Describe your product and what you want",
        placeholder=(
            "E.g., A red leather 3-seater modern sofa. "
            "Make it in a Christmas living room setting with snow visible through the window."
        ),
        height=120,
        help="Include both product details and your desired variation/theme. The AI will handle the rest."
    )

    st.markdown("---")

    # ------------------------------------------------
    # INPUT 3: Assets
    # ------------------------------------------------
    st.subheader("3. Upload Assets")
    uploaded_files = st.file_uploader(
        "Upload Reference Images",
        type=['png', 'jpg', 'jpeg', 'webp'],
        accept_multiple_files=True
    )

    # Show uploaded previews
    if uploaded_files:
        preview_cols = st.columns(min(len(uploaded_files), 5))
        for idx, f in enumerate(uploaded_files):
            with preview_cols[idx % 5]:
                st.image(f, caption=f.name, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------
    # SETTINGS: Aspect Ratio
    # ------------------------------------------------
    st.subheader("⚙️ Settings")
    selected_ratio_label = st.selectbox(
        "Aspect Ratio",
        list(ASPECT_RATIOS.keys()),
        index=0,
        help="Output image aspect ratio for Nano Banana Pro."
    )
    aspect_ratio = ASPECT_RATIOS[selected_ratio_label]

    st.markdown("---")

        # ------------------------------------------------
    # EXECUTION
    # ------------------------------------------------
    ready = bool(uploaded_files) and bool(user_specs.strip())

    if not ready:
        st.info("📋 Please provide specifications and upload at least one image to proceed.")

    if st.button("🚀 Generate Output", type="primary"):
        
        # Validate AFTER button click instead of disabling
        if not uploaded_files:
            st.warning("⚠️ Please upload at least one reference image.")
            st.stop()
        
        if not user_specs.strip():
            st.warning("⚠️ Please enter product specifications / requirements.")
            st.stop()

        workflow_name = current_op.get('workflow')
        workflow_module = WORKFLOW_MAP.get(workflow_name)

        if not workflow_module:
            st.error(f"Workflow '{workflow_name}' is not defined in WORKFLOW_MAP.")
            st.stop()

        # ------------------------------------------------
        # DEBUG PANEL
        # ------------------------------------------------
        with st.expander("🐛 Debug Panel — Pipeline Details", expanded=True):

            st.markdown("### 📥 Inputs Received")
            st.markdown(f"**Operation:** `[{current_op['id']}] {current_op['name']}`")
            st.markdown(f"**Workflow:** `{workflow_name}`")
            st.markdown(f"**Template File:** `{current_op.get('template')}`")
            st.markdown(f"**Aspect Ratio:** `{aspect_ratio}`")
            st.markdown(f"**Number of Assets:** `{len(uploaded_files)}`")
            st.markdown(f"**User Specs:**")
            st.code(user_specs, language="text")

            st.markdown("---")
            st.markdown("### ⚙️ Pipeline Execution Log")

        try:
            results = workflow_module.execute(
                uploaded_files=uploaded_files,
                user_specs=user_specs,
                template_filename=current_op.get('template'),
                aspect_ratio=aspect_ratio,
            )

            st.success(f"✅ Generation Complete! {len(results)} image(s) generated.")

            # ------------------------------------------------
            # RESULTS & LOCAL SAVE
            # ------------------------------------------------
            st.markdown("---")
            st.subheader("🖼️ Results")

            for idx, img in enumerate(results):
                col_img, col_info = st.columns([2, 1])

                with col_img:
                    st.image(img, caption=f"Result {idx + 1}", use_container_width=True)

                with col_info:
                    # Save locally
                    variant_name = sanitize_filename(user_specs)
                    save_path, filename = output_handler.save_image(
                        img,
                        current_op['name'],
                        variant_name
                    )

                    st.markdown(f"**💾 Saved Locally**")
                    st.code(save_path, language="text")
                    st.caption(f"📂 `outputs/{current_op['name']}/`")

                    st.download_button(
                        label="⬇️ Download",
                        data=output_handler.convert_to_bytes(img),
                        file_name=filename,
                        mime="image/png",
                        key=f"download_{idx}"
                    )

            # ------------------------------------------------
            # PAST GENERATIONS (for this operation)
            # ------------------------------------------------
            with st.expander(f"📁 All saved outputs for `{current_op['name']}`", expanded=False):
                past_outputs = output_handler.get_operation_outputs(current_op['name'])
                if past_outputs:
                    st.markdown(f"**{len(past_outputs)}** image(s) found")
                    history_cols = st.columns(min(len(past_outputs), 4))
                    for h_idx, item in enumerate(past_outputs[:12]):  # Show last 12
                        with history_cols[h_idx % 4]:
                            hist_img = Image.open(item["path"])
                            st.image(hist_img, caption=item["filename"], use_container_width=True)
                else:
                    st.info("No previous outputs found for this operation.")

        except Exception as e:
            st.error(f"❌ Execution Error: {e}")
            import traceback
            with st.expander("🔴 Full Error Traceback"):
                st.code(traceback.format_exc(), language="python")

if __name__ == "__main__":
    main()