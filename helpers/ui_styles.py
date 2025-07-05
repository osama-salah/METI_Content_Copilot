"""
UI styles and CSS configuration for the RoboGarden Instructor Copilot.
This module contains all the styling and theming logic for the Streamlit application.
"""

import streamlit as st


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

        /* Selectbox styling */
        .stSelectbox>div>div>select {
            border-radius: 15px;
            border: 2px solid #3f7cac; /* Robo-Blue from logo */
            background-color: #ffffff;
            color: #3f7cac;
            font-family: 'Fredoka One', cursive;
            font-size: 14px;
            padding: 10px 15px;
        }
        .stSelectbox>div>div>select:focus {
            border-color: #8bc53f; /* Robo-Green from logo */
            outline: none;
        }

        /* File uploader styling */
        .stFileUploader>div>div>div>button {
            border-radius: 15px;
            border: 2px solid #3f7cac; /* Robo-Blue from logo */
            background-color: #ffffff;
            color: #3f7cac;
            font-family: 'Fredoka One', cursive;
            font-size: 14px;
            padding: 10px 15px;
            transition: all 0.3s ease-in-out;
        }
        .stFileUploader>div>div>div>button:hover {
            background-color: #3f7cac; /* Robo-Blue from logo */
            color: #ffffff;
        }

        /* Input field styling */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            border-radius: 15px;
            border: 2px solid #3f7cac; /* Robo-Blue from logo */
            background-color: #ffffff;
            color: #3f7cac;
            font-family: 'Fredoka One', cursive;
            font-size: 14px;
            padding: 10px 15px;
        }
        .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
            border-color: #8bc53f; /* Robo-Green from logo */
            outline: none;
        }

        /* Sidebar styling */
        .stSidebar {
            background-color: #ffffff;
            border-radius: 15px;
            border: 2px solid #3f7cac; /* Robo-Blue from logo */
            margin: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stSidebar .stSelectbox>div>div>select {
            border-radius: 10px;
            border: 2px solid #3f7cac; /* Robo-Blue from logo */
            background-color: #ffffff;
            color: #3f7cac;
            font-family: 'Fredoka One', cursive;
            font-size: 12px;
            padding: 8px 12px;
        }

        /* Progress bar styling */
        .stProgress>div>div>div>div {
            background-color: #8bc53f; /* Robo-Green from logo */
            border-radius: 10px;
        }

        /* Message styling */
        .stSuccess {
            background-color: #8bc53f; /* Robo-Green from logo */
            color: #ffffff;
            border-radius: 15px;
            padding: 15px;
            font-family: 'Fredoka One', cursive;
            font-size: 14px;
            border: 2px solid #8bc53f;
        }

        .stError {
            background-color: #e53238; /* Robo-Red from logo */
            color: #ffffff;
            border-radius: 15px;
            padding: 15px;
            font-family: 'Fredoka One', cursive;
            font-size: 14px;
            border: 2px solid #e53238;
        }

        .stInfo {
            background-color: #3f7cac; /* Robo-Blue from logo */
            color: #ffffff;
            border-radius: 15px;
            padding: 15px;
            font-family: 'Fredoka One', cursive;
            font-size: 14px;
            border: 2px solid #3f7cac;
        }

        /* Metric styling */
        .stMetric {
            background-color: #ffffff;
            border-radius: 15px;
            border: 2px solid #3f7cac; /* Robo-Blue from logo */
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stMetric>div>div>div {
            font-family: 'Fredoka One', cursive;
            color: #3f7cac; /* Robo-Blue from logo */
        }

        /* Divider styling */
        .stDivider {
            border-top: 3px solid #ffc300; /* Canary-Yellow from logo */
            margin: 20px 0;
        }

        /* Expander styling */
        .stExpander {
            background-color: #ffffff;
            border-radius: 15px;
            border: 2px solid #3f7cac; /* Robo-Blue from logo */
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stExpander>div>div>div>div {
            font-family: 'Fredoka One', cursive;
            color: #3f7cac; /* Robo-Blue from logo */
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #ffffff;
            border-radius: 15px;
            border: 2px solid #3f7cac; /* Robo-Blue from logo */
            padding: 5px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stTabs [data-baseweb="tab"] {
            font-family: 'Fredoka One', cursive;
            color: #3f7cac; /* Robo-Blue from logo */
            border-radius: 10px;
            padding: 8px 16px;
            margin: 2px;
            border: 2px solid transparent;
            background-color: transparent;
            transition: all 0.3s ease-in-out;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #8bc53f; /* Robo-Green from logo */
            color: #ffffff;
            border-color: #8bc53f;
        }
        .stTabs [aria-selected="true"] {
            background-color: #ffc300; /* Canary-Yellow from logo */
            color: #ffffff;
            border-color: #ffc300;
        }

        /* Download button styling */
        .stDownloadButton>button {
            font-family: 'Fredoka One', cursive;
            border: 2px solid #8bc53f; /* Robo-Green from logo */
            border-radius: 25px;
            color: #ffffff;
            background-color: #8bc53f; /* Robo-Green from logo */
            padding: 12px 28px;
            font-size: 16px;
            font-weight: bold;
            text-transform: uppercase;
            transition: all 0.3s ease-in-out;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stDownloadButton>button:hover {
            transform: translateY(-2px);
            background-color: #3f7cac; /* Robo-Blue from logo */
            color: white;
            border-color: #3f7cac;
            box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        }

        /* Warning styling */
        .stWarning {
            background-color: #ffc300; /* Canary-Yellow from logo */
            color: #ffffff;
            border-radius: 15px;
            padding: 15px;
            font-family: 'Fredoka One', cursive;
            font-size: 14px;
            border: 2px solid #ffc300;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def add_header_image():
    """Add the header image to the application"""
    try:
        st.image("static/banner.jpg", width=800)
    except:
        # If banner image doesn't exist, show a placeholder
        st.markdown("## 🤖 RoboGarden Instructor Copilot")
