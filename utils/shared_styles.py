# utils/shared_styles.py

def load_css():
    return """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
        
        /* עיצוב כפתורי הרדיו */
        div.row-widget.stRadio > div {
            display: flex;
            justify-content: center;
            gap: 2rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        div.row-widget.stRadio > div label {
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        div.row-widget.stRadio > div label:hover {
            background: #e9ecef;
        }
        
        /* עיצוב אזור העלאת קבצים */
        .stFileUploader {
            padding: 2rem;
            border: 2px dashed #dee2e6;
            border-radius: 10px;
            text-align: center;
        }
        
        /* עיצוב תמונות הדוגמה */
        div.column-widget.stImage {
            margin-bottom: 1rem;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* עיצוב כפתורי בחירת תמונה */
        .stButton > button {
            width: 100%;
            margin-top: 0.5rem;
            margin-bottom: 1.5rem;
        }

        /* Modern Image Container Styling */
        .stImage {
            position: relative;
            overflow: hidden;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: all 0.3s ease-in-out;
        }

        .stImage:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }

        /* Image Effect */
        .stImage img {
            transition: all 0.5s ease-in-out;
            backface-visibility: hidden;
        }

        .stImage:hover img {
            transform: scale(1.02);
        }
    </style>
    """

def load_js():
    return """
    <script>
        // Your JavaScript code here
    </script>
    """

def apply_styles():
    """Apply all shared styles and JS"""
    import streamlit as st
    
    # Apply CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Apply JS
    st.markdown(load_js(), unsafe_allow_html=True)