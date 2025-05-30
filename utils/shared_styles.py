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
            color: white !important;  /* Changed caption buttons to white */
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

        /* New WhatsApp button styling */
        .whatsapp-section button {
            background: linear-gradient(45deg, #25d366, #128C7E) !important;
            color: white !important;
            border: none !important;
            font-weight: bold !important;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease !important;
            animation: whatsapp-pulse 2s infinite;
        }

        .whatsapp-section button:before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(120deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shine 3s infinite;
        }

        @keyframes whatsapp-pulse {
            0% {
                box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.4);
            }
            70% {
                box-shadow: 0 0 0 10px rgba(37, 211, 102, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(37, 211, 102, 0);
            }
        }

        @keyframes shine {
            0% { left: -100%; }
            20% { left: 100%; }
            100% { left: 100%; }
        }

        .whatsapp-section button:hover {
            transform: scale(1.05) !important;
            box-shadow: 0 8px 15px rgba(37, 211, 102, 0.3) !important;
        }
        
        /* Button hover and click animations */
        .stButton > button {
            transition: all 0.3s ease;
            transform-origin: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            background-color: #4CAF50 !important;
        }
        
        .stButton > button:active {
            transform: translateY(1px) scale(0.98);
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        
        /* Custom sections styling with hover effects */
        .custom-section {
            transition: all 0.3s ease;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 2px solid transparent;
        }
        
        .custom-section:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        }
        
        .style-section {
            background-color: #f0f8ff;
        }
        
        .style-section:hover {
            border-color: #1e88e5;
        }
        
        .whatsapp-section {
            background-color: #e8f5e9;
        }
        
        .whatsapp-section:hover {
            border-color: #2e7d32;
        }
        
        /* Selectbox hover effect */
        .stSelectbox:hover {
            border-color: #1e88e5;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Input field hover effect */
        .stTextInput:hover {
            border-color: #2e7d32;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Title animation */
        .title-animation {
            animation: fadeInUp 0.5s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
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