"""
Content Reviewer tab component for the RoboGarden Instructor Copilot.
This module handles validating and improving existing courses.
"""

import streamlit as st
import json
from helpers.text_utils import extract_text_from_files
from helpers import prompt_utils
from helpers.file_generators import create_styled_pdf, create_styled_docx, DOWNLOAD_ENABLED


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
