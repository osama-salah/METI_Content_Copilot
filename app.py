import streamlit as st
import google.generativeai as genai
from io import BytesIO
import re

# --- Optional dependencies for download functionality ---
try:
    from fpdf import FPDF
    import docx
    from docx.shared import Pt
    DOWNLOAD_ENABLED = True
except ImportError:
    DOWNLOAD_ENABLED = False

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

# --- Helper functions for file creation with Markdown parsing ---

def create_styled_docx(text):
    """Generates a DOCX file from a Markdown string with styling for headers, lists, and code."""
    doc = docx.Document()
    in_code_block = False
    code_block_started = False  # Track if we just started a code block
    
    for line in text.split('\n'):
        # Code block handling
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                # Only add spacing before code block if the previous element wasn't empty
                code_block_started = True
            else:
                # Add some spacing after code block
                doc.add_paragraph()
                code_block_started = False
            continue

        if in_code_block:
            # For code blocks, add paragraph with shaded background
            p = doc.add_paragraph(line)
            p.style = 'No Spacing'
            
            # Set font for code
            if p.runs:
                font = p.runs[0].font
            else:
                run = p.add_run('')
                font = run.font
            font.name = 'Courier New'
            font.size = Pt(10)
            
            # Add shaded background to the paragraph
            from docx.oxml.shared import qn
            from docx.oxml import parse_xml
            
            # Create shading element with light gray background
            shading_elm = parse_xml(r'<w:shd {} w:fill="F0F0F0"/>'.format(
                'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
            ))
            p._element.get_or_add_pPr().append(shading_elm)
            
            # Add border around code block paragraphs
            from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
            p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
            
            # Set paragraph spacing for code blocks
            paragraph_format = p.paragraph_format
            paragraph_format.left_indent = Pt(12)  # Slight indentation
            paragraph_format.right_indent = Pt(12)
            
            # Only add space before the first line of the code block
            if code_block_started:
                paragraph_format.space_before = Pt(6)
                code_block_started = False
            else:
                paragraph_format.space_before = Pt(2)
            
            paragraph_format.space_after = Pt(2)
            
            continue

        # Other markdown handling
        line = line.strip()
        if line.startswith('# '):
            doc.add_heading(line[2:], level=1)
        elif line.startswith('## '):
            doc.add_heading(line[3:], level=2)
        elif line.startswith('### '):
            doc.add_heading(line[4:], level=3)
        elif line.startswith(('* ', '- ')):
            p = doc.add_paragraph(style='List Bullet')
            # Handle inline styles (bold, italic, code)
            parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|\`.*?\`)', line[2:])
            for part in parts:
                if not part: continue
                if part.startswith('**') and part.endswith('**'):
                    p.add_run(part[2:-2]).bold = True
                elif part.startswith('*') and part.endswith('*'):
                    p.add_run(part[1:-1]).italic = True
                elif part.startswith('`') and part.endswith('`'):
                    run = p.add_run(part[1:-1])
                    run.font.name = 'Courier New'
                    # Add light gray background for inline code
                    from docx.oxml.shared import qn
                    from docx.oxml import parse_xml
                    shading_elm = parse_xml(r'<w:shd {} w:fill="E8E8E8"/>'.format(
                        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
                    ))
                    run._element.get_or_add_rPr().append(shading_elm)
                else:
                    p.add_run(part)
        elif line:
            p = doc.add_paragraph()
            # Handle inline styles (bold, italic, code)
            parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|\`.*?\`)', line)
            for part in parts:
                if not part: continue
                if part.startswith('**') and part.endswith('**'):
                    p.add_run(part[2:-2]).bold = True
                elif part.startswith('*') and part.endswith('*'):
                    p.add_run(part[1:-1]).italic = True
                elif part.startswith('`') and part.endswith('`'):
                    run = p.add_run(part[1:-1])
                    run.font.name = 'Courier New'
                    # Add light gray background for inline code
                    from docx.oxml.shared import qn
                    from docx.oxml import parse_xml
                    shading_elm = parse_xml(r'<w:shd {} w:fill="E8E8E8"/>'.format(
                        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
                    ))
                    run._element.get_or_add_rPr().append(shading_elm)
                else:
                    p.add_run(part)

    doc_fp = BytesIO()
    doc.save(doc_fp)
    doc_fp.seek(0)
    return doc_fp.getvalue()



def process_pdf_inline_styles(pdf, line, indent):
    """Helper to process a line with inline markdown for PDF `write` method, handling wrapping."""
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|\`.*?\`)', line)
    for part in parts:
        if not part: continue
        
        style = ''
        font = 'Arial'
        size = 12
        if part.startswith('**') and part.endswith('**'):
            content = part[2:-2]
            style = 'B'
        elif part.startswith('*') and part.endswith('*'):
            content = part[1:-1]
            style = 'I'
        elif part.startswith('`') and part.endswith('`'):
            content = part[1:-1]
            font = 'Courier'
            style = ''
            size = 10
        else:
            content = part
        
        pdf.set_font(font, style, size)
        
        # Manual word wrapping for the `write` method
        words = content.split(' ')
        for word in words:
            word_to_write = word + ' '
            word_width = pdf.get_string_width(word_to_write)
            if pdf.get_x() + word_width > pdf.w - pdf.r_margin:
                pdf.ln()
                pdf.set_x(indent) # Re-apply indent for wrapped line
            pdf.write(5, word_to_write.encode('latin-1', 'replace').decode('latin-1'))
    
    pdf.set_font('Arial', '', 12) # Reset font at the end of the line

def create_styled_pdf(text):
    """
    Generates a PDF file from a Markdown string with native styling
    for headers, lists, bold, italic, and code.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Add Unicode font support
    try:
        # Try to add a Unicode font (DejaVu Sans supports most Unicode characters)
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
        pdf.add_font('DejaVu', 'I', 'DejaVuSans-Oblique.ttf', uni=True)
        default_font = 'DejaVu'
        unicode_support = True
    except:
        # Fallback to Arial if Unicode fonts are not available
        default_font = 'Arial'
        unicode_support = False
    
    pdf.set_font(default_font, size=12)
    
    effective_page_width = pdf.w - 2 * pdf.l_margin

    in_code_block = False
    for line in text.split('\n'):
        # Code block handling
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                pdf.set_font('Courier' if not unicode_support else default_font, size=10)
                pdf.set_fill_color(240, 240, 240)
                pdf.ln(2)
            else:
                pdf.set_font(default_font, size=12)
                pdf.set_fill_color(255, 255, 255)
                pdf.ln(5)
            continue

        if in_code_block:
            # Fix: Ensure proper positioning for code block lines
            pdf.set_x(pdf.l_margin)  # Reset X position to left margin
            safe_line = line if unicode_support else line.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(effective_page_width, 5, safe_line, border=0, fill=True)
            continue

        # Other markdown handling
        line = line.strip()
        if not line:
            pdf.ln(5)
            continue

        if line.startswith('# '):
            pdf.set_font(default_font, 'B', 16)
            safe_text = line[2:].strip() if unicode_support else line[2:].strip().encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(effective_page_width, 8, safe_text)
            pdf.ln(4)
        elif line.startswith('## '):
            pdf.set_font(default_font, 'B', 14)
            safe_text = line[3:].strip() if unicode_support else line[3:].strip().encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(effective_page_width, 7, safe_text)
            pdf.ln(3)
        elif line.startswith('### '):
            pdf.set_font(default_font, 'B', 12)
            safe_text = line[4:].strip() if unicode_support else line[4:].strip().encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(effective_page_width, 6, safe_text)
            pdf.ln(2)
        elif line.startswith(('* ', '- ')):
            pdf.set_x(pdf.l_margin)  # Ensure proper positioning for list items
            initial_x = pdf.get_x()
            
            # Use a safe bullet character based on font support
            bullet_char = '•' if unicode_support else '- '
            safe_bullet = bullet_char if unicode_support else bullet_char.encode('latin-1', 'replace').decode('latin-1')
            
            pdf.write(5, safe_bullet)
            process_pdf_inline_styles(pdf, line[2:].strip(), initial_x + 5, unicode_support, default_font)
            pdf.ln()
        else:
            pdf.set_x(pdf.l_margin)  # Ensure proper positioning for regular paragraphs
            process_pdf_inline_styles(pdf, line, pdf.l_margin, unicode_support, default_font)
            pdf.ln()

    pdf_fp = BytesIO()
    pdf.output(pdf_fp)
    pdf_fp.seek(0)
    return pdf_fp.getvalue()



def process_pdf_inline_styles(pdf, line, indent, unicode_support=False, default_font='Arial'):
    """Helper to process a line with inline markdown for PDF `write` method, handling wrapping."""
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|\`.*?\`)', line)
    for part in parts:
        if not part: continue
        
        style = ''
        font = default_font
        size = 12
        if part.startswith('**') and part.endswith('**'):
            content = part[2:-2]
            style = 'B'
        elif part.startswith('*') and part.endswith('*'):
            content = part[1:-1]
            style = 'I'
        elif part.startswith('`') and part.endswith('`'):
            content = part[1:-1]
            font = 'Courier' if not unicode_support else default_font
            style = ''
            size = 10
        else:
            content = part
        
        pdf.set_font(font, style, size)
        
        # Handle Unicode encoding
        safe_content = content if unicode_support else content.encode('latin-1', 'replace').decode('latin-1')
        
        # Manual word wrapping for the `write` method
        words = safe_content.split(' ')
        for word in words:
            word_to_write = word + ' '
            word_width = pdf.get_string_width(word_to_write)
            if pdf.get_x() + word_width > pdf.w - pdf.r_margin:
                pdf.ln()
                pdf.set_x(indent)
            pdf.write(5, word_to_write)
    
    pdf.set_font(default_font, '', 12)



# Page Configuration
st.set_page_config(layout="wide", page_title="RoboGarden AI Content Creator")

# --- Initialize Session State ---
if 'generated_course_text' not in st.session_state:
    st.session_state.generated_course_text = ""


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
            padding-top: 1rem; /* Reduced padding */
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
if not DOWNLOAD_ENABLED:
    st.warning("Please install `fpdf2` and `python-docx` to enable download functionality (`pip install fpdf2 python-docx`).")


try:
    st.image("static/images/banner2.png", use_container_width=True)
except Exception:
    st.info("Banner image not found. Please add banner2.png to the static/images directory.")

# --- App Header ---
st.title("AI Content Generator 🤖")
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
                                st.session_state.generated_course_text = response.text # Save to session state
                            else:
                                st.warning("HMM! Could not extract text from the uploaded files. Please check the files and try again.")
                                st.session_state.generated_course_text = ""
                        except Exception as e:
                            st.error(f"An error occurred during generation: {e}")
                            st.session_state.generated_course_text = ""
            else:
                st.warning("Please upload at least one document to start building.")
    
    with col2:
        if not st.session_state.generated_course_text:
            st.info("Your generated course will appear here once you click the generate button.")
        else:
            st.success("YEAAH! Your course is ready!")
            st.markdown(st.session_state.generated_course_text) # Display from session state
            
            st.markdown("---") # Separator

            # Add download buttons if libraries are installed
            if DOWNLOAD_ENABLED:
                dl_col_1, dl_col_2, dl_col_3 = st.columns([2,2,2])
                with dl_col_1:
                    pdf_bytes = create_styled_pdf(st.session_state.generated_course_text)
                    st.download_button(
                        label="⬇️ Download as PDF",
                        data=pdf_bytes,
                        file_name="generated_course.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                with dl_col_2:
                    docx_bytes = create_styled_docx(st.session_state.generated_course_text)
                    st.download_button(
                        label="⬇️ Download as DOCX",
                        data=docx_bytes,
                        file_name="generated_course.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
            
            # Button to clear the state and start over
            if st.button("Generate New Course", use_container_width=False):
                st.session_state.generated_course_text = ""
                st.rerun()


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
