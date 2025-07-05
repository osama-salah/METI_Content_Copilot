"""
UI components for the RoboGarden Instructor Copilot.
This module contains all the tab components and their associated functionality.
"""

import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json
import re
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
    
    # Initialize session state for validation results
    if 'validation_issues' not in st.session_state:
        st.session_state.validation_issues = []
    if 'original_content' not in st.session_state:
        st.session_state.original_content = ""
    if 'selected_corrections' not in st.session_state:
        st.session_state.selected_corrections = {}
    
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
                    # Extract text with formatting preserved (now contains markdown)
                    formatted_text = extract_text_from_files([uploaded_file_val])                     
                    if formatted_text.strip():
                        st.session_state.original_content = formatted_text
                        prompt = prompt_utils.create_validation_prompt(formatted_text)
                        response = model.generate_content(prompt, request_options={'timeout': 600})
                        
                        # Parse JSON response
                        try:
                            # Clean the response text to extract JSON
                            response_text = response.text.strip()
                            if response_text.startswith('```json'):
                                response_text = response_text[7:]
                            if response_text.endswith('```'):
                                response_text = response_text[:-3]
                            
                            issues = json.loads(response_text)
                            st.session_state.validation_issues = issues
                            st.session_state.selected_corrections = {i: False for i in range(len(issues))}
                            st.success("YEAAH! Validation complete.")
                            st.session_state.corrected_content = None
                        except json.JSONDecodeError as e:
                            st.error(f"Could not parse validation results: {e}")
                            st.text("Raw response:")
                            st.text(response.text)
                    else:
                        st.warning("HMM! Could not extract text from the uploaded file.")
                except Exception as e:
                    st.error(f"An error occurred during validation: {e}")
        else:
            st.warning("Please upload a document to validate.")
    
    # Display validation results if available
    if st.session_state.get('validation_issues', None):
        st.markdown("---")
        st.subheader("Validation Results")
        
        # Selection buttons
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("Select All", key="select_all", use_container_width=True):
                for i in range(len(st.session_state.validation_issues)):
                    st.session_state.selected_corrections[i] = True
                st.rerun()
        
        with col2:
            if st.button("Select None", key="select_none", use_container_width=True):
                for i in range(len(st.session_state.validation_issues)):
                    st.session_state.selected_corrections[i] = False
                st.rerun()
        
        # Display issues table with checkboxes
        st.markdown("### Issues Found")
        
        # Custom CSS for better table styling
        st.markdown("""
        <style>
        .issue-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .issue-table th, .issue-table td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
            vertical-align: top;
        }
        .issue-table th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .issue-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .issue-quote {
            font-style: italic;
            background-color: #f0f0f0;
            padding: 8px;
            border-radius: 4px;
            margin: 4px 0;
        }
        .correction-text {
            background-color: #e8f5e8;
            padding: 8px;
            border-radius: 4px;
            margin: 4px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        for i, issue in enumerate(st.session_state.validation_issues):
            # Create checkbox for each issue
            checkbox_col, content_col = st.columns([1, 10])
            
            with checkbox_col:
                selected = st.checkbox(
                    f"Apply #{i+1}", 
                    key=f"checkbox_{i}",
                    value=st.session_state.selected_corrections.get(i, False)
                )
                st.session_state.selected_corrections[i] = selected
            
            with content_col:
                st.markdown(f"**Issue #{i+1}:**")
                st.markdown(f"**Original Text:** *{issue['original_text']}*")
                st.markdown(f"**Explanation:** {issue['explanation']}")
                st.markdown(f"**Suggested Correction:** {issue['suggested_correction']}")
                st.markdown("---")
        
        # Apply corrections button and debug toggle
        col_apply, col_debug = st.columns([5, 1])
        with col_apply:
            apply_clicked = st.button("🔧 Apply Selected Corrections 🔧", use_container_width=True, key="apply_corrections")
        with col_debug:
            debug_mode = st.checkbox("Debug", key="debug_mode")
        
        if apply_clicked:
            selected_issues = [i for i, selected in st.session_state.selected_corrections.items() if selected]
            
            if selected_issues:
                with st.spinner("Applying selected corrections..."):
                    try:
                        corrected_content = st.session_state.original_content
                        applied_count = 0
                        debug_info = []
                        
                        # Apply corrections in reverse order to maintain text positions
                        for i in reversed(selected_issues):
                            issue = st.session_state.validation_issues[i]
                            original_text = issue['original_text'].strip()
                            suggested_correction = issue['suggested_correction'].strip()
                            
                            if debug_mode:
                                debug_info.append(f"**Issue #{i+1}:**")
                                debug_info.append(f"Looking for: `{original_text[:100]}...`")
                            
                            # Try multiple matching strategies with safety checks
                            applied = False
                            
                            # Strategy 1: Exact match (safest)
                            if original_text in corrected_content:
                                # Count occurrences to ensure we're not replacing too much
                                occurrence_count = corrected_content.count(original_text)
                                if occurrence_count == 1:
                                    # Safe to replace - only one occurrence
                                    corrected_content = corrected_content.replace(original_text, suggested_correction, 1)
                                    applied_count += 1
                                    applied = True
                                    if debug_mode:
                                        debug_info.append("✅ Applied using exact match")
                                elif occurrence_count > 1:
                                    if debug_mode:
                                        debug_info.append(f"⚠️ Skipped - found {occurrence_count} occurrences (ambiguous)")
                            
                            # Strategy 2: Try with length-similar matching and context validation
                            elif not applied:
                                # More conservative approach - find text with similar length and structure
                                original_words = original_text.split()
                                if len(original_words) >= 3:  # Only try for reasonably long phrases
                                    
                                    # Look for sequences that start and end with the same words
                                    start_word = original_words[0]
                                    end_word = original_words[-1]
                                    
                                    # Find all occurrences of the start word
                                    start_positions = []
                                    start_idx = 0
                                    while True:
                                        start_idx = corrected_content.find(start_word, start_idx)
                                        if start_idx == -1:
                                            break
                                        start_positions.append(start_idx)
                                        start_idx += 1
                                    
                                    # For each start position, check if we can find a valid end
                                    for start_pos in start_positions:
                                        end_pos = corrected_content.find(end_word, start_pos + len(start_word))
                                        if end_pos != -1:
                                            end_pos += len(end_word)
                                            candidate_text = corrected_content[start_pos:end_pos]
                                            
                                            # Validate the candidate: similar length and word count
                                            candidate_words = candidate_text.split()
                                            length_ratio = len(candidate_text) / len(original_text)
                                            word_ratio = len(candidate_words) / len(original_words)
                                            
                                            # Only accept if length and word count are reasonably similar
                                            if (0.7 <= length_ratio <= 1.5 and 
                                                0.8 <= word_ratio <= 1.2 and
                                                len(candidate_words) >= 3):
                                                
                                                # Additional check: at least 50% of words should match
                                                original_words_lower = [w.lower() for w in original_words]
                                                candidate_words_lower = [w.lower() for w in candidate_words]
                                                
                                                matching_words = sum(1 for w in original_words_lower 
                                                                   if w in candidate_words_lower)
                                                match_ratio = matching_words / len(original_words_lower)
                                                
                                                if match_ratio >= 0.5:  # At least 50% word overlap
                                                    corrected_content = corrected_content.replace(candidate_text, suggested_correction, 1)
                                                    applied_count += 1
                                                    applied = True
                                                    if debug_mode:
                                                        debug_info.append(f"✅ Applied using fuzzy match (similarity: {match_ratio:.2f})")
                                                        debug_info.append(f"   Original: `{original_text[:50]}...`")
                                                        debug_info.append(f"   Found: `{candidate_text[:50]}...`")
                                                    break
                            
                            # Strategy 3: Very conservative partial matching for short phrases only
                            if not applied and len(original_text.split()) <= 3 and len(original_text) >= 10:
                                # Only for very short, specific phrases
                                # Look for the phrase in a way that won't damage the document
                                
                                # Split into sentences and paragraphs for safer replacement
                                paragraphs = corrected_content.split('\n\n')
                                found_and_replaced = False
                                
                                for p_idx, paragraph in enumerate(paragraphs):
                                    if original_text.lower() in paragraph.lower():
                                        # Find the exact case-insensitive match
                                        lower_para = paragraph.lower()
                                        lower_original = original_text.lower()
                                        
                                        match_start = lower_para.find(lower_original)
                                        if match_start != -1:
                                            actual_text = paragraph[match_start:match_start + len(original_text)]
                                            
                                            # Only replace if it's a whole word/phrase match
                                            # Check boundaries
                                            char_before = paragraph[match_start - 1] if match_start > 0 else ' '
                                            char_after = paragraph[match_start + len(original_text)] if match_start + len(original_text) < len(paragraph) else ' '
                                            
                                            if (char_before in ' \n\t.,!?;:' and 
                                                char_after in ' \n\t.,!?;:'):
                                                
                                                paragraphs[p_idx] = paragraph.replace(actual_text, suggested_correction, 1)
                                                corrected_content = '\n\n'.join(paragraphs)
                                                applied_count += 1
                                                applied = True
                                                found_and_replaced = True
                                                if debug_mode:
                                                    debug_info.append("✅ Applied using conservative word-boundary matching")
                                                break
                                
                                if not found_and_replaced and debug_mode:
                                    debug_info.append("❌ Could not safely apply this correction")
                            
                            elif not applied and debug_mode:
                                debug_info.append("❌ Could not apply this correction - too risky or no match found")
                                debug_info.append("")
                        
                        # Show debug information
                        if debug_mode and debug_info:
                            st.markdown("### Debug Information")
                            for info in debug_info:
                                st.text(info)
                        
                        st.session_state.corrected_content = corrected_content
                        if applied_count > 0:
                            st.success(f"Applied {applied_count} out of {len(selected_issues)} corrections successfully!")
                        else:
                            st.warning("No corrections could be applied. The original text might not match exactly. Enable debug mode to see more details.")
                        
                    except Exception as e:
                        st.error(f"Error applying corrections: {e}")
            else:
                st.warning("Please select at least one correction to apply.")
    
    # Display corrected content if available
    if st.session_state.get('corrected_content', None):
        st.markdown("---")
        st.subheader("Corrected Content")
        
        # Debug: Show what we're working with
        debug_content = st.checkbox("Show debug info", key="debug_content")
        if debug_content:
            st.text("Original content (first 700 chars):")
            st.text(st.session_state.original_content[:700])
            st.text("Corrected content (first 700 chars):")
            st.text(st.session_state.corrected_content[:700])
            
            # Show specific lines to debug markdown
            st.text("Corrected content line by line (first 10 lines):")
            lines = st.session_state.corrected_content.split('\n')[:10]
            for i, line in enumerate(lines):
                st.text(f"Line {i}: '{line}'")
        
        # Display the corrected content with proper markdown rendering
        st.markdown(st.session_state.corrected_content)
        
        # Download buttons for corrected content
        if DOWNLOAD_ENABLED:
            st.markdown("---")
            dl_col_1, dl_col_2, dl_col_3 = st.columns(3)
            
            with dl_col_1:
                pdf_bytes = create_styled_pdf(st.session_state.corrected_content)
                st.download_button(
                    label="⬇️ Download Corrected as PDF",
                    data=pdf_bytes,
                    file_name="corrected_course.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            with dl_col_2:
                docx_bytes = create_styled_docx(st.session_state.corrected_content)
                st.download_button(
                    label="⬇️ Download Corrected as DOCX",
                    data=docx_bytes,
                    file_name="corrected_course.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )       

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
