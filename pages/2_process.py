# pages/2_✨_process.py
import streamlit as st
from deep_translator import GoogleTranslator
import json
from utils.pollinations_generator import PollinationsGenerator
from utils.shared_styles import apply_styles

@st.cache_data
def load_styles():
    """Load and sort styles"""
    try:
        with open('data/image_styles.json', 'r', encoding='utf-8') as f:
            styles = json.load(f).get('styles', [])
            free_style = [style for style in styles if style['name'] == "סגנון חופשי"]
            other_styles = [style for style in styles if style['name'] != "סגנון חופשי"]
            sorted_other_styles = sorted(other_styles, key=lambda x: x['name'])
            return free_style + sorted_other_styles
    except Exception as e:
        st.error(f"שגיאה בטעינת הסגנונות: {e}")
        return []

def translate(text, target='en'):
    """Translate text using Google Translator"""
    if not text:
        return ""
    try:
        translator = GoogleTranslator(source='auto', target=target)
        return translator.translate(text)
    except Exception as e:
        st.error(f"שגיאה בתרגום: {e}")
        return text

def generate_image_with_style(style, prompt):
    """Generate image with selected style"""
    if not prompt:
        st.warning("נא להוסיף תיאור לתמונה")
        return False
        
    full_prompt = f"{style['prompt_prefix']} {translate(prompt, 'en')}"
    st.session_state.prompt = prompt
    st.session_state.selected_style = style['name']
    
    with st.toast('אני יוצר את הקסם... (זה יכול לקחת עד 30 שניות)'):
    # with st.spinner('אני יוצר את הקסם... (זה יכול לקחת עד 30 שניות)'):
        generator = PollinationsGenerator()
        model = style.get('model', 'flux')
        
        st.session_state.generated_image = generator.generate_image(full_prompt, model)
        if st.session_state.generated_image:
            st.session_state.state['image_processed'] = True
            return True
        else:
            st.error('אירעה שגיאה ביצירת התמונה - נסו שוב.')
            return False

def main():
    # Apply shared styles including button effects
    apply_styles()
    st.markdown("""
        <style>
            /* Remove extra margins and padding */
            .stButton {
                margin: 0 !important;
                padding: 0 !important;
            }
            
            /* Style the button itself */
            .stButton > button {
                margin: 2px 0 !important;
                padding: 10px !important;
                width: 100% !important;
                border-radius: 8px !important;
                background-color: #2196F3 !important;
                color: white !important;
                height: auto !important;
                min-height: 40px !important;
            }
            
            /* Remove column gap */
            div.row-widget.stHorizontal > div {
                margin-bottom: 0 !important;
                padding: 0 5px !important;
            }
            
            /* Fix vertical spacing */
            div.element-container {
                margin: 1px !important;
                padding: 0 !important;
            }
            
            /* Container styling */
            .style-container {
                padding: 1rem;
                border-radius: 10px;
                margin: 0.5rem 0;
                background-color: #f8f9fa;
            }
            
            /* Remove extra padding from columns */
            div.stColumn {
                padding: 0 5px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Check page state
    if not st.session_state.state.get('image_uploaded'):
        st.session_state.state['current_page'] = '1_upload'
        st.rerun()
        return
    
    if not st.session_state.get('selected_image'):
        st.warning("נא להעלות תמונה קודם")
        return

    # Optional: Add button to start over
    if st.button("להתחיל מחדש 🔄"):
        st.session_state.state['current_page'] = '1_upload'
        st.session_state.state['image_uploaded'] = False
        st.session_state.state['image_processed'] = False
        st.session_state.state['prompt'] = False
        st.session_state.state['selected_style'] = False
        st.session_state.selected_image = None
        st.session_state.generated_image = None
        st.rerun()
        
    # st.markdown("""
    #     <div class='style-container'>
    #         <h3 style='color: #1e88e5; text-align: center; margin: 0;'>התמונה שבחרתם 🖼️</h3>
    #     </div>
    # """, unsafe_allow_html=True)
    
    st.image(st.session_state.selected_image, use_container_width=True)

    styles = load_styles()

    # st.markdown("""
    #     <div class='style-container'>
    #         <h3 style='color: #1e88e5; margin: 0;'>✨ בואו נהפוך את התמונה ליצירת אמנות ✨</h3>
    #     </div>
    # """, unsafe_allow_html=True)

    with st.spinner('אני קורא את תוכן התמונה...'):
        prompt = st.text_area(
            "תיאור התמונה",
            value=translate(st.session_state.image_description, 'iw'),
            height=200,
            placeholder="תוכלו לערוך את התיאור כרצונכם..."
        )

    st.markdown("""
        <div class='style-container'>
            <h3 style='color: #1e88e5; text-align: center; margin: 0;'>בחרו סגנון ליצירת התמונה 🎨</h3>
            <p style='text-align: center; color: #666; margin: 0.5rem 0 0 0;'>כל כפתור יוצר את התמונה בסגנון שונה</p>
        </div>
    """, unsafe_allow_html=True)

    # Create compact grid for style buttons
    cols = st.columns(2)
    for idx, style in enumerate(styles):
        with cols[idx % 2]:
            if st.button(
                f"{style['name']}",
                key=f"style_{idx}",
                use_container_width=True
            ):
                if generate_image_with_style(style, prompt):
                    st.rerun()

    # Handle successful generation
    if st.session_state.generated_image:
        st.session_state.state['image_processed'] = True
        st.session_state.state['current_page'] = '3_result'
        st.rerun()

if __name__ == "__main__":
    main()