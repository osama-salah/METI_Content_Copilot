"""
Course Architect tab component for the RoboGarden Instructor Copilot.
This module handles building new course TOCs from scratch.
"""

import streamlit as st
from helpers.text_utils import extract_text_from_files
from helpers import prompt_utils
from helpers.file_generators import create_styled_pdf, create_styled_docx, create_descriptive_filename, DOWNLOAD_ENABLED


def course_architect_tab(model):
    """Course Architect tab - Build a new course TOC from scratch"""
    st.header("Build a New Course TOC from Scratch")
    st.markdown("Upload your raw materials (like lecture notes, articles, or a textbook chapter) and let the AI build a structured course for you.")
    
    col1, col2 = st.columns([1, 2])  # [sidebar_width, main_content_width]
    
    with col1:
        st.subheader("Blueprint 📝")
        
        uploaded_files_gen = st.file_uploader(
            "Upload your content here", 
            accept_multiple_files=True,
            type=['pdf', 'docx', 'txt'],
            key="gen_uploader"
        )
        
        course_length = st.selectbox("Course Length", ["Quick (Overview)", "Moderate (Standard)", "Detailed (In-depth)"], key="gen_length")
        target_audience = st.selectbox("Target Audience", ["High School Students", "Undergraduate Students", "Industry Professionals", "General Public"], key="gen_audience")
        course_tone = st.selectbox("Tone of Voice", ["Formal & Academic", "Conversational & Friendly", "Technical & Precise"], key="gen_tone")
        
        if st.button("✨ Generate Course ✨", use_container_width=True, key="gen_button"):
            if uploaded_files_gen:
                with col2:
                    with st.spinner("Analyzing documents and designing your course... This is where the magic happens! 🪄"):
                        try:
                            raw_text = extract_text_from_files(uploaded_files_gen)                            
                            if raw_text.strip():
                                prompt = prompt_utils.create_generation_prompt(raw_text, course_length, target_audience, course_tone)
                                response = model.generate_content(prompt, request_options={'timeout': 600})
                                st.session_state.generated_course_text = response.text  # Save to session state
                                st.session_state.generated_quiz_text = ""  # Clear any existing quiz
                            else:
                                st.warning("HMM! Could not extract text from the uploaded files. Please check the files and try again.")
                                st.session_state.generated_course_text = ""
                                st.session_state.generated_quiz_text = ""
                        except Exception as e:
                            st.error(f"An error occurred during generation: {e}")
                            st.session_state.generated_course_text = ""
                            st.session_state.generated_quiz_text = ""
            else:
                st.warning("Please upload at least one document to start building.")

        # Quiz Creator Panel - Only show if course is generated
        if st.session_state.generated_course_text:
            st.markdown("---")
            st.subheader("Quiz Creator 🧠")
            
            quiz_type = st.radio("Quiz Type:", 
                               ["Multiple Choice", "True/False", "Short Answer", "Mixed"], 
                               key="course_quiz_type")
            
            quiz_difficulty = st.radio("Difficulty Level:",
                                     ["Easy", "Medium", "Hard", "Mixed"], 
                                     key="course_quiz_difficulty")
            
            # Custom styling for quiz button
            st.markdown('<div class="quiz-button">', unsafe_allow_html=True)
            if st.button("🧠 Generate Comprehensive Quiz 🧠", use_container_width=True, key="course_quiz_button"):
                with col2:
                    with st.spinner("Crafting your quiz from the generated course... 📝"):
                        try:
                            prompt = prompt_utils.create_quiz_creator_prompt(
                                st.session_state.generated_course_text, 
                                difficulty_level=quiz_difficulty, 
                                question_type=quiz_type
                            )
                            response = model.generate_content(prompt, request_options={'timeout': 600})
                            st.session_state.generated_quiz_text = response.text
                        except Exception as e:
                            st.error(f"An error occurred during quiz creation: {e}")
                            st.session_state.generated_quiz_text = ""
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if not st.session_state.generated_course_text:
            st.info("Your generated course will appear here once you click the generate button.")
        else:
            st.success("YEAAH! Your course is ready!")
            st.markdown(st.session_state.generated_course_text)  # Display from session state
            
            st.markdown("---")  # Separator

            # Add download buttons if libraries are installed
            if DOWNLOAD_ENABLED:
                user_params = {
                    'audience': target_audience,
                    'length': course_length,
                }
                
                dl_col_1, dl_col_2, dl_col_3 = st.columns([2, 2, 2])
                with dl_col_1:
                    pdf_bytes = create_styled_pdf(st.session_state.generated_course_text)
                    course_filename = create_descriptive_filename(
                        "Course", 
                        user_params, 
                        st.session_state.generated_course_text, 
                        "pdf"
                    )
                    st.download_button(
                        label="⬇️ Download as PDF",
                        data=pdf_bytes,
                        file_name=course_filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                with dl_col_2:
                    docx_bytes = create_styled_docx(st.session_state.generated_course_text)
                    course_docx_filename = create_descriptive_filename(
                        "Course", 
                        user_params, 
                        st.session_state.generated_course_text, 
                        "docx"
                    )
                    st.download_button(
                        label="⬇️ Download as DOCX",
                        data=docx_bytes,
                        file_name=course_docx_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                        
            # Button to clear the state and start over
            if st.button("Generate New Course", use_container_width=False):
                st.session_state.generated_course_text = ""
                st.session_state.generated_quiz_text = ""
                st.rerun()

            # Display generated quiz if available
            if st.session_state.generated_quiz_text:
                st.markdown("---")
                st.markdown(st.session_state.generated_quiz_text, unsafe_allow_html=True)
                
            # Quiz download buttons
            if DOWNLOAD_ENABLED and st.session_state.generated_quiz_text:
                quiz_params = {
                    'audience': target_audience,
                    'quiz_type': quiz_type,
                    'difficulty': quiz_difficulty
                }
                
                quiz_dl_col_1, quiz_dl_col_2, quiz_dl_col_3 = st.columns([2, 2, 1])
                with quiz_dl_col_1:
                    quiz_pdf_bytes = create_styled_pdf(st.session_state.generated_quiz_text)
                    quiz_filename = create_descriptive_filename(
                        "Quiz", 
                        quiz_params, 
                        st.session_state.generated_quiz_text, 
                        "pdf"
                    )
                    st.download_button(
                        label="⬇️ PDF",
                        data=quiz_pdf_bytes,
                        file_name=quiz_filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                with quiz_dl_col_2:
                    quiz_docx_bytes = create_styled_docx(st.session_state.generated_quiz_text)
                    quiz_docx_filename = create_descriptive_filename(
                        "Quiz", 
                        quiz_params, 
                        st.session_state.generated_quiz_text, 
                        "docx"
                    )
                    st.download_button(
                        label="⬇️ DOCX",
                        data=quiz_docx_bytes,
                        file_name=quiz_docx_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
