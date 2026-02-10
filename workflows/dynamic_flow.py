# workflows/dynamic_flow.py
import streamlit as st
from utils import file_io, llm_client, image_client, preprocessing


def execute(uploaded_files, user_specs, template_filename, **kwargs):
    """
    WORKFLOW: Dynamic Prompting
    Uses Gemini Flash (LLM) to write a detailed Meta-Prompt, then generates.
    All reference images are sent together in a single generation call.
    """
    aspect_ratio = kwargs.get("aspect_ratio", "1:1")

    # 1. Load the System Instruction Template
    system_template = file_io.load_template(template_filename)

    # DEBUG: Show loaded template
    with st.expander("📄 Loaded Template", expanded=False):
        st.code(system_template, language="text")

    # 2. Process ALL uploaded images
    st.markdown("#### 📎 Processing Assets")
    pil_images = []
    for img_file in uploaded_files:
        pil_image = preprocessing.process_upload(img_file)
        pil_images.append(pil_image)

    # DEBUG: Show all input images
    preview_cols = st.columns(min(len(pil_images), 5))
    for idx, img in enumerate(pil_images):
        with preview_cols[idx % 5]:
            st.image(img, caption=f"Asset {idx + 1}: {uploaded_files[idx].name}", use_container_width=True)

    st.markdown(f"**Total assets loaded:** `{len(pil_images)}`")
    st.markdown("---")

    # 3. LLM Step: Create the Meta-Prompt (ALL images sent together)
    with st.status("🤖 Step 1 — LLM generating MetaPrompt...", expanded=True):

        # DEBUG: Show what's being sent to LLM
        st.markdown("**📤 LLM Input:**")
        st.markdown(f"- Template: `{template_filename}`")
        st.markdown(f"- User Specs: `{user_specs[:150]}...`" if len(user_specs) > 150 else f"- User Specs: `{user_specs}`")
        st.markdown(f"- Reference Images: `{len(pil_images)}` image(s)")
        for idx, f in enumerate(uploaded_files):
            st.markdown(f"  - Asset {idx + 1}: `{f.name}`")

        meta_prompt = llm_client.generate_meta_prompt(
            user_specs=user_specs,
            template_text=system_template,
            user_images_pil=pil_images  # ✅ ALL images at once
        )

        # DEBUG: Show generated MetaPrompt
        st.markdown("**📥 Generated MetaPrompt:**")
        st.code(meta_prompt, language="text")

    # 4. Image Gen Step: Call Nano Banana Pro (ALL images sent together)
    with st.status("🎨 Step 2 — Nano Banana Pro generating image...", expanded=True):

        # DEBUG: Show what's being sent to image model
        st.markdown("**📤 Image Model Input:**")
        st.markdown(f"- MetaPrompt length: `{len(meta_prompt)} chars`")
        st.markdown(f"- Reference images: `{len(pil_images)}`")
        st.markdown(f"- Aspect Ratio: `{aspect_ratio}`")

        result_image = image_client.generate_image(
            meta_prompt=meta_prompt,
            reference_images_pil=pil_images,  # ✅ ALL images at once
            aspect_ratio=aspect_ratio
        )

        # DEBUG: Confirm generation
        if result_image:
            st.markdown("**✅ Image generated successfully**")
            st.image(result_image, caption="Generated Output", width=400)
        else:
            st.markdown("**❌ No image returned from model**")

    if result_image:
        return [result_image]
    else:
        return []