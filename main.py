# main.py [the template page]
import streamlit as st
import importlib
import os
from datetime import datetime
import pytz
from utils.counter import increment_user_count, get_user_count
from utils.init import initialize
from utils.shared_styles import apply_styles


# Set page config for better mobile responsiveness
st.set_page_config(
    layout="wide", 
    initial_sidebar_state="collapsed", 
    page_title="מחולל התמונות החכם",
    page_icon="📷"
)

# Initialize session state if not exists
if 'state' not in st.session_state:
    st.session_state.state = {
        'counted': False,
        'current_page': '1_upload',  # Add this to track current page
        'image_uploaded': False,
        'image_processed': False
        # 'prompt': False,
        # 'selected_style': False,
    }

# Initialize other session state variables
for key in ['generated_image', 'selected_image', 'image_description', 'prompt', 'selected_style']:
    st.session_state.setdefault(key, None if key != 'image_description' else "")

def hide_streamlit_header_footer():
    hide_st_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
    </style>
    """
    st.markdown(hide_st_style, unsafe_allow_html=True)

def load_html_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        return f.read()
    
def main():
    # Apply shared styles
    # apply_styles()
    
    with st.spinner('האפליקציה נטענת...'):
        title, image_path, footer_content = initialize()
        # st.title("🎨 מחולל התמונות החכם")
        hide_streamlit_header_footer()        

        # Load and display the custom expander HTML
        expander_html = load_html_file('expander.html')
        st.markdown(expander_html, unsafe_allow_html=True)            

        #### Import and run the pages ###
        try:
            upload_page = st.session_state.state['current_page']
            upload_page = importlib.import_module("pages." + upload_page)
            upload_page.main()
            
        except Exception as e:
            st.error(f"Error loading upload page: {e}")
        ### End the container ###

    # Display footer content
    st.markdown(footer_content, unsafe_allow_html=True)    

    # Display user count
    user_count = get_user_count(formatted=True)
    print(user_count)
    st.markdown(f"<p class='user-count' style='color: #4B0082;'>סה\"כ משתמשים: {user_count}</p>", unsafe_allow_html=True)

    # Display and update last datetime use
    last_datetime_use = os.getenv("LAST_DATETIME_USE")
    st.markdown(f"<p class='last-datetime-use'>משתמש אחרון נכנס ב {last_datetime_use}</p>", unsafe_allow_html=True)

    # Update LAST_DATETIME_USE on first visit
    if 'initial_visit' not in st.session_state:
        st.session_state.initial_visit = True
        israel_time = datetime.now(pytz.timezone("Asia/Jerusalem"))
        formatted_time = israel_time.strftime("%d/%m/%Y %H:%M")
        os.environ['LAST_DATETIME_USE'] = formatted_time

if __name__ == "__main__":
    # Increment user count on first load
    if 'counted' not in st.session_state:
        st.session_state.counted = True
        increment_user_count()
    
    main()