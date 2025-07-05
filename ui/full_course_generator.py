"""
Full Course Generator tab component for the RoboGarden Instructor Copilot.
This module handles building complete courses from scratch.
"""

import streamlit as st
from helpers.text_utils import extract_text_from_files
from helpers import prompt_utils
from helpers.file_generators import create_styled_pdf, create_styled_docx, create_descriptive_filename, DOWNLOAD_ENABLED


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
