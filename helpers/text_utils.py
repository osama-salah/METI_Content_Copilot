import streamlit as st
import PyPDF2
import docx
import io

def extract_text_from_files(uploaded_files):
    """Reads and extracts text from uploaded PDF, DOCX, and TXT files."""
    full_text = ""
    if not uploaded_files:
        return ""
    
    for file in uploaded_files:
        try:
            # Move the file pointer back to the beginning before reading
            file.seek(0)
            if file.type == "application/pdf":
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.getvalue()))
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n\n"
            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = docx.Document(io.BytesIO(file.getvalue()))
                for para in doc.paragraphs:
                    full_text += para.text + "\n"
            elif file.type == "text/plain":
                full_text += file.getvalue().decode("utf-8") + "\n\n"
        except Exception as e:
            st.error(f"Error reading file {file.name}: {e}")
    return full_text