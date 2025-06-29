import streamlit as st
import google.generativeai as genai


# Ensure st is available globally before importing helpers
try:
    from helpers.text_utils import extract_text_from_files
    from helpers import prompt_utils
except NameError as e:
    st.error(f"Import error in helper modules: {e}")
    st.error("Make sure all helper modules that use 'st' have 'import streamlit as st' at the top")
    st.stop()
except Exception as e:
    st.error(f"Unexpected import error: {e}")
    st.stop()

# Page Configuration
st.set_page_config(layout="wide", page_title="AI Instructional Design Assistant")

# --- Styling (Inspired by the uploaded image) ---
def load_css():
    css = """
    <style>
        /* Import a playful, rounded font */
        @import url('https://fonts.googleapis.com/css2?family=Carter+One&display=swap');

        /* Main app background */
        .stApp {
            background-color: #FAF3E0; /* Sandy beige */
        }

        /* Titles and headers */
        h1, h2, h3 {
            font-family: 'Carter One', cursive;
            color: #5D4037; /* Dark earthy brown */
        }

        /* Buttons */
        .stButton>button {
            border: 2px solid #5D4037;
            border-radius: 20px;
            color: #5D4037;
            background-color: #FFD700; /* Gold/Yellow */
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.3s ease-in-out;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            background-color: #FFA500; /* Orange */
            color: white;
            border-color: #FFA500;
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #FDF5E6;
            border-radius: 8px 8px 0px 0px;
            gap: 10px;
            padding-top: 10px;
            padding-bottom: 10px;
            color: #5D4037 !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #00CED1; /* Cyan */
            color: white !important;
            font-weight: bold;
        }
        
        /* Sidebar styling */
        .stSidebar {
            background-color: #FDF5E6;
            border-right: 2px solid #EAE0C8;
        }

        /* Main content area styling */
        .main .block-container {
            padding-top: 2rem;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

load_css()

# --- App Header ---
st.title("AI Instructional Design Assistant ✨")
st.write("Your creative partner for building amazing educational content!")

# --- API Key Check and Model Initialization ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    if not api_key:
        st.error("API key not found. Please set your GOOGLE_API_KEY in Streamlit secrets.")
        st.stop()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Failed to configure Google AI: {e}")
    st.stop()


# --- Main Application Tabs ---
tab1, tab2, tab3, tab4 = st.tabs([
    "### 🤖 Course Architect", 
    "### 🧐 Pedagogical Proofreader", 
    "### 🚀 Future-Proofing Engine",
    "### 🛠️ Quiz Creator"
])

# --- TAB 1: Course Architect ---
with tab1:
    st.header("Build a New Course from Scratch")
    st.markdown("Upload your raw materials (like lecture notes, articles, or a textbook chapter) and let the AI build a structured course for you.")
    
    col1, col2 = st.columns([1, 2]) # [sidebar_width, main_content_width]
    
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
                                st.success("YEAAH! Your course is ready!")
                                st.markdown(response.text)
                            else:
                                st.warning("HMM! Could not extract text from the uploaded files. Please check the files and try again.")
                        except Exception as e:
                            st.error(f"An error occurred during generation: {e}")
            else:
                st.warning("Please upload at least one document to start building.")
    
    with col2:
        st.info("Your generated course will appear here once you click the generate button.")


# --- TAB 2: Pedagogical Proofreader ---
with tab2:
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

# --- TAB 3: Future-Proofing Engine ---
with tab3:
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

# --- TAB 4: Quiz Creator ---
with tab4:
    st.header("Create a Quiz for Your Course")
    st.markdown("Upload your course content, and the AI will generate a comprehensive quiz to test understanding and retention.")
    st.radio("Select the type of quiz you want to create:", 
             ["Multiple Choice", "True/False", "Short Answer","Mixed"], 
             key="quiz_type")
    
    st.radio("Select the difficulty level of the quiz:",
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
                        prompt = prompt_utils.create_quiz_creator_prompt(raw_text,difficulty_level=st.session_state.quiz_difficulty, question_type=st.session_state.quiz_type)
                        response = model.generate_content(prompt, request_options={'timeout': 600})
                        st.success("YEAAH! Your quiz is ready!")
                        st.html(response.text)
                    else:
                        st.warning("HMM! Could not extract text from the uploaded file.")
                except Exception as e:
                    st.error(f"An error occurred during quiz creation: {e}")
        else:
            st.warning("Please upload a document to create a quiz.")