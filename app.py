import streamlit as st
import google.generativeai as genai

# Ensure st is available globally before importing helpers
try:
    from helpers.text_utils import extract_text_from_files
    from helpers import prompt_utils
except ImportError:
    # Creating dummy functions if helpers are not available
    # This allows the app to run without the helper files for styling purposes.
    st.warning("Helper modules (helpers.text_utils, helpers.prompt_utils) not found. Using dummy functions. App functionality will be limited.")
    def extract_text_from_files(files):
        return " ".join([file.name for file in files])
    class PromptUtils:
        def create_generation_prompt(self, *args): return "Dummy generation prompt"
        def create_validation_prompt(self, *args): return "Dummy validation prompt"
        def create_updater_prompt(self, *args): return "Dummy updater prompt"
        def create_quiz_creator_prompt(self, *args): return "Dummy quiz prompt"
    prompt_utils = PromptUtils()

except NameError as e:
    st.error(f"Import error in helper modules: {e}")
    st.error("Make sure all helper modules that use 'st' have 'import streamlit as st' at the top")
    st.stop()
except Exception as e:
    st.error(f"Unexpected import error: {e}")
    st.stop()

# Page Configuration
st.set_page_config(layout="wide", page_title="RoboGarden AI")

# --- Styling (Inspired by the uploaded images) ---
def load_css():
    """
    Loads custom CSS to style the Streamlit application according to the RoboGarden theme.
    Colors are extracted from the provided banner.jpg and colors.png.
    - Canary Yellow (#ffc300)
    - Blue (#3f7cac)
    - Green (#8bc53f)
    - Red (#e53238)
    - Light Background (#ecffd6)
    """
    css = """
    <style>
        /* Import a playful, rounded font that matches the banner's style */
        @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&display=swap');

        /* Main app background */
        .stApp {
            background-color: #ecffd6; /* A clean, light background */
        }
        
        /* Add the banner image to the top of the main content area */
        .main .block-container:first-child::before {
            content: '';
            display: block;
            height: 200px; /* Adjust height as needed */
            background-size: cover;
            background-position: center;
            border-radius: 10px;
            margin-bottom: 2rem;
        }

        /* Main title styling */
        .main h1:first-of-type {
            font-family: 'Fredoka One', cursive;
            color: #8bc53f; /* Robo-Green from logo */
        }

        /* Other titles and headers */
        h1:not(.main h1:first-of-type), h2, h3 {
            font-family: 'Fredoka One', cursive;
            color: #3f7cac; /* Robo-Blue from logo */
        }

        /* Buttons */
        .stButton>button {
            font-family: 'Fredoka One', cursive;
            border: 2px solid #ffc300; /* Canary-Yellow from logo */
            border-radius: 25px;
            color: #ffffff;
            background-color: #ffc300; /* Canary-Yellow from logo */
            padding: 12px 28px;
            font-size: 16px;
            font-weight: bold;
            text-transform: uppercase;
            transition: all 0.3s ease-in-out;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            background-color: #8bc53f; /* Robo-Green from logo */
            color: white;
            border-color: #8bc53f;
            box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px; /* Reduce gap between tabs */
            border-bottom: 3px solid #3f7cac; /* Blue underline for the tab bar */
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #eaf4fc; /* Lighter Blue Accent */
            border-radius: 8px 8px 0px 0px;
            gap: 10px;
            padding: 10px 20px;
            color: #3f7cac !important;
            font-family: 'Fredoka One', cursive;
            margin: 0;
        }
        .stTabs [aria-selected="true"] {
            background-color: #3f7cac; /* Robo-Blue */
            color: white !important;
            font-weight: bold;
        }
        
        /* Sidebar/Column styling for controls */
        div[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
             background-color: #fff9e6; /* Light Yellow to match buttons */
             border-radius: 10px;
             padding: 20px;
        }

        /* Main content area styling */
        .main .block-container {
            padding-top: 2rem;
        }
        
        /* Success/Info/Warning boxes */
        .stAlert {
            border-radius: 10px;
            border-width: 2px;
        }
        
        /* Style for success messages to use the green color */
        .stAlert[data-baseweb="notification-positive"] {
            border-color: #8bc53f;
        }
        
        /* Style for warning messages to use the red color */
        .stAlert[data-baseweb="notification-negative"] {
             border-color: #e53238;
        }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


load_css()

try:
    st.image("static/images/banner2.png", use_container_width=True)
except FileNotFoundError:
    st.info("Banner image not found. Please add banner.jpg to the root directory.")

# --- App Header ---
st.title(" AI Content Generator 🤖")
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
