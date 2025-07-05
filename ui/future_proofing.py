"""
Future Proofing tab component for the RoboGarden Instructor Copilot.
This module handles updating courses with the latest trends.
"""

import streamlit as st
from helpers.text_utils import extract_text_from_files
from helpers import prompt_utils


def future_proofing_tab(model):
    """Future-Proofing Engine tab - Update a course with latest trends"""
    st.header("Update a Course with the Latest Trends")
    st.markdown("Is your content still current? Upload a course, and the AI will scan the horizon for new trends, technologies, and research, suggesting relevant updates.")

    uploaded_file_upd = st.file_uploader(
        "Upload your course document to update", 
        accept_multiple_files=False, 
        type=['pdf', 'docx', 'txt'],
        key="upd_uploader"
    )

    if st.button("🚀 Future-Proof Course 🚀", use_container_width=True, key="upd_button"):
        if uploaded_file_upd:
            with st.spinner("Scanning the future for updates... 📡"):
                try:
                    raw_text = extract_text_from_files([uploaded_file_upd])
                    if raw_text.strip():
                        prompt = prompt_utils.create_updater_prompt(raw_text)
                        response = model.generate_content(prompt, request_options={'timeout': 600})
                        st.success("YEAAH! Here are the suggested updates.")
                        st.markdown(response.text)
                    else:
                        st.warning("HMM! Could not extract text from the uploaded file.")
                except Exception as e:
                    st.error(f"An error occurred during the update process: {e}")
        else:
            st.warning("Please upload a document to update.")
