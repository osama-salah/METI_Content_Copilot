"""
UI components for the RoboGarden Instructor Copilot.
This module contains all the tab components and their associated functionality.
"""

import streamlit as st
import google.generativeai as genai
from datetime import datetime
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
            if st.button("🧠 Generate Quiz 🧠", use_container_width=True, key="course_quiz_button"):
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


def content_reviewer_tab(model):
    """Content Reviewer tab - Validate and improve an existing course"""
    st.header("Validate and Improve an Existing Course")
    st.markdown("Upload a complete course document. The AI will act as a pedagogical expert, checking for clarity, engagement, and style issues.")
    
    uploaded_file_val = st.file_uploader(
        "Upload your course document here", 
        accept_multiple_files=False, 
        type=['pdf', 'docx', 'txt'],
        key="val_uploader"
    )

    if st.button("🔍 Validate Course 🔍", use_container_width=True, key="val_button"):
        if uploaded_file_val:
            with st.spinner("Our expert is proofreading your course... 🧐"):
                try:
                    raw_text = extract_text_from_files([uploaded_file_val])
                    if raw_text.strip():
                        prompt = prompt_utils.create_validation_prompt(raw_text)
                        response = model.generate_content(prompt, request_options={'timeout': 600})
                        st.success("YEAAH! Validation complete.")
                        st.markdown(response.text)
                    else:
                        st.warning("HMM! Could not extract text from the uploaded file.")
                except Exception as e:
                    st.error(f"An error occurred during validation: {e}")
        else:
            st.warning("Please upload a document to validate.")


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


def full_course_generator_tab(model):
    """Full Course Generator tab - Build a complete course from scratch"""
    st.header("Build a New Course from Scratch")
    st.markdown("Upload your raw materials (like lecture notes, articles, or a textbook chapter) and let the AI build a structured course for you.")
    
    col1, col2 = st.columns([1, 2])  # [sidebar_width, main_content_width]
    
    with col1:
        st.subheader("Blueprint 📝")
        
        uploaded_files_gen = st.file_uploader(
            "Upload your content here", 
            accept_multiple_files=True,
            type=['pdf', 'docx', 'txt'],
            key="full_course_uploader"
        )

        course_length = st.selectbox("Course Length", ["Quick (Overview)", "Moderate (Standard)", "Detailed (In-depth)"], key="gen_length_5")
        target_audience = st.selectbox("Target Audience", ["High School Students", "Undergraduate Students", "Industry Professionals", "General Public"], key="gen_audience_5")
        course_tone = st.selectbox("Tone of Voice", ["Formal & Academic", "Conversational & Friendly", "Technical & Precise"], key="gen_tone_5")
        
        if st.button("✨ Generate Full Course Content ✨", use_container_width=True, key="gen_button_2"):
            if uploaded_files_gen:
                with col2:
                    with st.spinner("Analyzing documents and designing your full course... This may take a few minutes 🪄"):
                        try:
                            raw_text = extract_text_from_files(uploaded_files_gen)
                            if raw_text.strip():
                                # Initialize container for full course content
                                full_course_content = ""
                                
                                # Store content sections separately
                                if 'course_sections' not in st.session_state:
                                    st.session_state.course_sections = {}
                                
                                # Step 1: Generate Table of Contents
                                st.info("Step 1/3: Generating table of contents...")
                                toc_prompt = f"""
                                Based on the following materials, create a detailed table of contents for a {course_length} course targeted at {target_audience} with a {course_tone} tone.
                                Create a well-structured course with 3-5 main lessons. Include lesson titles and 3-5 subtopics for each lesson.
                                Format as a proper Markdown table of contents with # for main lesson titles and ## for subtopics.
                                
                                Materials:
                                {raw_text[:10000]}
                                """
                                toc_response = model.generate_content(toc_prompt, request_options={'timeout': 300})
                                table_of_contents = toc_response.text
                                full_course_content += "# Course Table of Contents\n\n" + table_of_contents + "\n\n"
                                
                                # Store the table of contents section
                                st.session_state.course_sections["Table of Contents"] = table_of_contents
                                
                                # Extract lesson titles
                                lesson_titles = []
                                for line in table_of_contents.split('\n'):
                                    if line.strip().startswith('# '):
                                        lesson_titles.append(line.strip()[2:])
                                
                                # Step 2: Generate each lesson content with its quiz
                                st.info(f"Step 2/3: Generating {len(lesson_titles)} lessons with quizzes...")
                                progress_bar = st.progress(0)
                                
                                for idx, title in enumerate(lesson_titles):
                                    # Generate lesson content
                                    lesson_prompt = f"""
                                    Create detailed content for the lesson titled "{title}" for a {course_length} course targeted at {target_audience}.
                                    Use a {course_tone} tone. Include explanations, examples, and key concepts.
                                    Format using Markdown with proper headings, bullet points, and emphasis where appropriate.
                                    Base the content on these materials:
                                    
                                    {raw_text[:15000]}
                                    """
                                    lesson_response = model.generate_content(lesson_prompt, request_options={'timeout': 300})
                                    lesson_content = lesson_response.text
                                    full_course_content += f"\n\n# {title}\n\n{lesson_content}\n\n"
                                    
                                    # Store this lesson's content
                                    st.session_state.course_sections[f"Lesson {idx+1}: {title}"] = lesson_content
                                    
                                    # Immediately generate quiz for this lesson
                                    st.info(f"Creating quiz for lesson: {title}")
                                    quiz_prompt = prompt_utils.create_quiz_creator_prompt(
                                        lesson_content,
                                        difficulty_level="Medium", 
                                        question_type="Mixed"
                                    )
                                    quiz_response = model.generate_content(quiz_prompt, request_options={'timeout': 300})
                                    quiz_content = quiz_response.text
                                    full_course_content += f"\n\n## Quiz: {title}\n\n{quiz_content}\n\n"
                                    
                                    # Store this quiz's content
                                    st.session_state.course_sections[f"Quiz {idx+1}: {title}"] = quiz_content
                                    
                                    # Update progress bar
                                    progress_bar.progress((idx + 1) / len(lesson_titles))
                                
                                # Add "Full Course" option which contains everything
                                st.session_state.course_sections["Full Course"] = full_course_content
                                
                                # Save to session state
                                st.session_state.generated_course_text = full_course_content
                                st.session_state.course_generated = True
                                
                                # Display success message
                                st.success("✅ Full course generation complete with table of contents, lessons, and quizzes!")
                                
                            else:
                                st.warning("Could not extract text from the uploaded files. Please check the files and try again.")
                        except Exception as e:
                            st.error(f"An error occurred during generation: {e}")
            else:
                st.warning("Please upload at least one document to start building your course.")
    
    with col2:
        if 'course_generated' in st.session_state and st.session_state.course_generated:
            # Create a dropdown to select what content to view
            section_options = list(st.session_state.course_sections.keys())
            selected_section = st.selectbox("Choose what to view:", section_options)
            
            # Display the selected section
            st.markdown(st.session_state.course_sections[selected_section])
            
            # Add download buttons
            user_params = {
                'audience': st.session_state.get('gen_audience_5', 'General'),
                'length': st.session_state.get('gen_length_5', 'Standard'),
            }
            
            # Determine if we're downloading the full course or a section
            download_content = st.session_state.course_sections[selected_section]
            section_name = selected_section.replace(" ", "_").replace(":", "")
            
            if DOWNLOAD_ENABLED:
                dl_col_1, dl_col_2 = st.columns(2)
                with dl_col_1:
                    pdf_bytes = create_styled_pdf(download_content)
                    course_filename = create_descriptive_filename(
                        section_name, 
                        user_params, 
                        download_content, 
                        "pdf"
                    )
                    st.download_button(
                        label=f"⬇️ Download {selected_section} as PDF",
                        data=pdf_bytes,
                        file_name=course_filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                with dl_col_2:
                    docx_bytes = create_styled_docx(download_content)
                    course_docx_filename = create_descriptive_filename(
                        section_name, 
                        user_params, 
                        download_content, 
                        "docx"
                    )
                    st.download_button(
                        label=f"⬇️ Download {selected_section} as DOCX",
                        data=docx_bytes,
                        file_name=course_docx_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
        else:
            st.info("Your generated course will appear here once you click the generate button.")
