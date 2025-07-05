"""
RoboGarden Instructor Copilot - Main Application
A Streamlit application for creating educational content using AI.
"""

import streamlit as st
import google.generativeai as genai

# Import helper modules
try:
    from helpers.text_utils import extract_text_from_files
    from helpers import prompt_utils
    from helpers.ui_styles import load_css, add_header_image
    from helpers.ui_components import (
        course_architect_tab, 
        content_reviewer_tab, 
        future_proofing_tab, 
        quiz_creator_tab, 
        full_course_generator_tab
    )
    from helpers.file_generators import DOWNLOAD_ENABLED
except ImportError as e:
    st.error(f"Import error in helper modules: {e}")
    st.error("Make sure all helper modules are available and properly configured")
    st.stop()
except Exception as e:
    st.error(f"Unexpected import error: {e}")
    st.stop()

# Page Configuration
st.set_page_config(layout="wide", page_title="RoboGarden Instructor Copilot")
     
# --- Initialize Session State ---
if 'generated_course_text' not in st.session_state:
    st.session_state.generated_course_text = ""
if 'generated_quiz_text' not in st.session_state:
    st.session_state.generated_quiz_text = ""

# Load CSS and apply styling
load_css()

# Display download warning if needed
if not DOWNLOAD_ENABLED:
    st.warning("Please install `fpdf2` and `python-docx` to enable download functionality (`pip install fpdf2 python-docx`).")

# Add header image
add_header_image()

# --- App Header ---
st.title("RoboGarden Instructor Co-pilot🤖")
st.write("Your creative partner for building amazing educational content!")

# --- API Key Check and Model Initialization ---
try:
    # Use a dummy key if not found in secrets for graceful failure
    api_key = st.secrets.get("GOOGLE_API_KEY", "DUMMY_KEY_FOR_UI_DISPLAY")
    if api_key == "DUMMY_KEY_FOR_UI_DISPLAY":
        st.warning("API key not found. Please set your GOOGLE_API_KEY in Streamlit secrets. App is in read-only mode.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Failed to configure Google AI: {e}")
    st.stop()

# --- Main Application Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "### 🤖 Course Architect", 
    "### 🧐 Content Reviewer", 
    "### 🚀 Future-Proofing Engine",
    "### 🛠️ Quiz Creator",
    "### 📚 Full Course Generator"
])

# --- TAB CONTENT ---
with tab1:
    course_architect_tab(model)

with tab2:
    content_reviewer_tab(model)

with tab3:
    future_proofing_tab(model)

with tab4:
    quiz_creator_tab(model)

with tab5:
    full_course_generator_tab(model)
