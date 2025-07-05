"""
Quiz Creator tab component for the RoboGarden Instructor Copilot.
This module handles creating quizzes for courses.
"""

import streamlit as st
from helpers.text_utils import extract_text_from_files
from helpers import prompt_utils


def quiz_creator_tab(model):
    """Quiz Creator tab - Create a quiz for your course"""
    st.header("Create a Quiz for Your Course")
    st.markdown("Upload your course content, and the AI will generate a comprehensive quiz to test understanding and retention.")
    
    quiz_type = st.radio("Select the type of quiz you want to create:", 
                        ["Multiple Choice", "True/False", "Short Answer", "Mixed"], 
                        key="quiz_type")
    
    quiz_difficulty = st.radio("Select the difficulty level of the quiz:",
                              ["Easy", "Medium", "Hard", "Mixed"], 
                              key="quiz_difficulty")
    
    uploaded_file_quiz = st.file_uploader(
        "Upload your course document for quiz creation", 
        accept_multiple_files=False, 
        type=['pdf', 'docx', 'txt'],
        key="quiz_uploader"
    )

    if st.button("🛠️ Create Quiz 🛠️", use_container_width=True, key="quiz_button"):
        if uploaded_file_quiz:
            with st.spinner("Crafting your quiz... 📝"):
                try:
                    raw_text = extract_text_from_files([uploaded_file_quiz])
                    if raw_text.strip():
                        prompt = prompt_utils.create_quiz_creator_prompt(raw_text, difficulty_level=quiz_difficulty, question_type=quiz_type)
                        response = model.generate_content(prompt, request_options={'timeout': 600})
                        st.success("YEAAH! Your quiz is ready!")
                        st.markdown(response.text)
                    else:
                        st.warning("HMM! Could not extract text from the uploaded file.")
                except Exception as e:
                    st.error(f"An error occurred during quiz creation: {e}")
        else:
            st.warning("Please upload a document to create a quiz.")
