# pages/2_✨_process.py
import streamlit as st
from deep_translator import GoogleTranslator
import json
from utils.pollinations_generator import PollinationsGenerator

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

def main():
     # Check if we should be on this page
    if not st.session_state.state.get('image_uploaded'):
        st.session_state.state['current_page'] = '1_upload'
        st.rerun()
        return
    
    # Check if image is uploaded
    if not st.session_state.get('selected_image'):
        st.warning("נא להעלות תמונה קודם")
        return

    # Display selected image
    # body = "התמונה שנבחרה נשמרה בהצלחה, נמשיך לשלב הבא..."
    # st.toast(body, icon='🖼️')

    # st.subheader("התמונה שנבחרה 🖼️")
    st.image(st.session_state.selected_image, use_container_width=True)

    # Load styles
    styles = load_styles()

    # Process image
    with st.spinner('אני קורא את תוכן התמונה...'):
        prompt = st.text_area(
            "תיאור התמונה",
            value=translate(st.session_state.image_description, 'iw'),
            height=200
        )

    style = st.selectbox(
        "בחרו סגנון חדש לתמונה",
        [s['name'] for s in styles],
        index=0
    )

    if st.button("✨ לחצו עליי! ✨", type="primary") and prompt:
        st.session_state.prompt = prompt
        # print(st.session_state.prompt)
        selected_style = next(s for s in styles if s['name'] == style)
        full_prompt = f"{selected_style['prompt_prefix']} {translate(prompt, 'en')}"
        st.session_state.selected_style = selected_style['name']
        
        with st.spinner('אני יוצר את הקסם... (זה יכול לקחת עד 30 שניות)'):
            generator = PollinationsGenerator()
            model = selected_style.get('model', 'flux')
            
            st.session_state.generated_image = generator.generate_image(full_prompt, model)
            if st.session_state.generated_image:
                # st.success('יצרתי לכם תמונה חדשה מה אתם אומרים?')
                st.session_state.state['image_processed'] = True
                st.rerun()
            else:
                st.error('אירעה שגיאה ביצירת התמונה - נסו שוב ללחוץ על הכפתור.')

    # When generation is successful:
    if st.session_state.generated_image:
        st.session_state.state['image_processed'] = True
        st.session_state.state['current_page'] = '3_result'
        st.rerun()
if __name__ == "__main__":
    main()