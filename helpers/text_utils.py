import streamlit as st
import docx
import io
import re
try:
    import fitz  # pymupdf for better PDF text extraction with formatting
    PYMUPDF_AVAILABLE = True
except ImportError:
    import PyPDF2
    PYMUPDF_AVAILABLE = False

def extract_text_from_files(uploaded_files):
    """Reads and extracts text from uploaded PDF, DOCX, and TXT files with basic formatting preservation."""
    full_text = ""
    if not uploaded_files:
        return ""
    
    for file in uploaded_files:
        try:
            # Move the file pointer back to the beginning before reading
            file.seek(0)
            if file.type == "application/pdf":
                if PYMUPDF_AVAILABLE:
                    # Use pymupdf for better formatting extraction
                    pdf_document = fitz.open(stream=file.getvalue(), filetype="pdf")
                    for page_num in range(pdf_document.page_count):
                        page = pdf_document[page_num]
                        # Extract text with formatting information
                        page_text = extract_formatted_text_from_pdf_page(page)
                        if page_text:
                            full_text += page_text + "\n\n"
                    pdf_document.close()
                else:
                    # Fallback to PyPDF2
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.getvalue()))
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            # Basic formatting preservation for PDFs
                            page_text = preserve_basic_formatting(page_text)
                            full_text += page_text + "\n\n"
            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = docx.Document(io.BytesIO(file.getvalue()))
                for para in doc.paragraphs:
                    para_text = para.text
                    if para_text.strip():
                        # Convert basic Word formatting to markdown
                        para_text = convert_word_formatting_to_markdown(para, para_text)
                        full_text += para_text + "\n"
            elif file.type == "text/plain":
                content = file.getvalue().decode("utf-8")
                full_text += content + "\n\n"
        except Exception as e:
            st.error(f"Error reading file {file.name}: {e}")
    return full_text

def extract_formatted_text_from_pdf_page(page):
    """Extract text with formatting information using pymupdf."""
    blocks = page.get_text("dict")["blocks"]
    formatted_text = ""
    
    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                # Process spans individually to handle mixed formatting
                line_text = ""
                max_font_size = 0
                
                for span in line["spans"]:
                    text = span["text"]
                    font_size = span["size"]
                    font_flags = span["flags"]
                    
                    max_font_size = max(max_font_size, font_size)
                    
                    # Apply formatting to individual spans (trim spaces for proper markdown)
                    if font_flags & 2**4:  # Bold flag
                        trimmed_text = text.strip()
                        if trimmed_text:  # Only format non-empty text
                            # Preserve leading/trailing spaces outside the formatting
                            leading_space = text[:len(text) - len(text.lstrip())]
                            trailing_space = text[len(text.rstrip()):]
                            text = f"{leading_space}**{trimmed_text}**{trailing_space}"
                    elif font_flags & 2**6:  # Italic flag
                        trimmed_text = text.strip()
                        if trimmed_text:  # Only format non-empty text
                            leading_space = text[:len(text) - len(text.lstrip())]
                            trailing_space = text[len(text.rstrip()):]
                            text = f"{leading_space}*{trimmed_text}*{trailing_space}"
                    
                    line_text += text
                
                line_text = line_text.strip()
                
                if line_text:
                    # Only apply heading formatting if font size is large enough
                    if max_font_size > 20:  # Only very large text becomes H1
                        # Remove any existing formatting and make it a heading
                        clean_text = line_text.replace("**", "").replace("*", "")
                        line_text = f"# {clean_text}"
                    elif max_font_size > 18:  # Large text becomes H2
                        clean_text = line_text.replace("**", "").replace("*", "")
                        line_text = f"## {clean_text}"
                    elif max_font_size > 16:  # Medium-large text becomes H3
                        clean_text = line_text.replace("**", "").replace("*", "")
                        line_text = f"### {clean_text}"
                
                if line_text.strip():
                    # Ensure headers are on their own lines with proper spacing
                    if line_text.strip().startswith(('#', '##', '###')):
                        formatted_text += "\n" + line_text.strip() + "\n\n"
                    else:
                        formatted_text += line_text + "\n"
            
            if not formatted_text.endswith('\n\n'):
                formatted_text += "\n"  # Add paragraph break
    
    return formatted_text

def preserve_basic_formatting(text):
    """Convert common text patterns to markdown formatting."""
    # Convert common heading patterns
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            formatted_lines.append("")
            continue
            
        # Detect headings (lines in all caps or with specific patterns)
        if len(line) > 5 and line.isupper() and not line.endswith('.'):
            formatted_lines.append(f"## {line.title()}")
        # Detect numbered sections
        elif re.match(r'^\d+\.?\s+[A-Z]', line):
            formatted_lines.append(f"### {line}")
        # Detect bullet points
        elif re.match(r'^[\-\*•]\s+', line):
            formatted_lines.append(f"- {line[2:]}")
        # Detect numbered lists
        elif re.match(r'^\d+\.\s+', line):
            formatted_lines.append(f"1. {line[3:]}")
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def convert_word_formatting_to_markdown(paragraph, text):
    """Convert Word paragraph formatting to markdown."""
    # Check if this is a heading based on style name
    style_name = paragraph.style.name.lower()
    
    if 'heading 1' in style_name:
        return f"# {text}"
    elif 'heading 2' in style_name:
        return f"## {text}"
    elif 'heading 3' in style_name:
        return f"### {text}"
    elif 'heading 4' in style_name:
        return f"#### {text}"
    elif 'heading 5' in style_name:
        return f"##### {text}"
    elif 'heading 6' in style_name:
        return f"###### {text}"
    
    # Check for list items
    elif 'list' in style_name:
        if 'bullet' in style_name:
            return f"- {text}"
        else:
            return f"1. {text}"
    
    # Check for bold formatting in runs
    formatted_text = ""
    for run in paragraph.runs:
        run_text = run.text
        if run.bold:
            run_text = f"**{run_text}**"
        if run.italic:
            run_text = f"*{run_text}*"
        formatted_text += run_text
    
    return formatted_text if formatted_text else text