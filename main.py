import base64
import streamlit as st
import json
import os
from PIL import Image
from io import BytesIO
from utils.pollinations_generator import PollinationsGenerator
from utils.greenapi import WhatsAppSender
from utils.Hugging_Face_Transformer import ImageCaptioning
from deep_translator import GoogleTranslator

# הגדרת עיצוב הדף
st.set_page_config(page_title="מחולל התמונות החכם", page_icon="🎨", layout="wide")

# CSS מותאם אישית
st.markdown("""
    <style>
        .stButton>button { width: 100%; height: 3rem; font-size: 1.2rem; margin-top: 1rem; }
        .st-emotion-cache-1v0mbdj > img { width: 100%; max-width: 300px; }
        .upload-text { font-size: 1.2rem; text-align: center; margin: 1rem 0; }
    </style>
""", unsafe_allow_html=True)

# איתחול session state
for key in ['generated_image', 'selected_image', 'image_description']:
    st.session_state.setdefault(key, None if key != 'image_description' else "")

def translate(text, target='en'):
    try:
        return GoogleTranslator(source='auto', target=target).translate(text)
    except Exception as e:
        st.error(f"שגיאה בתרגום: {e}")
        return text

def process_image(image_data):
    """עיבוד תמונה ל-BytesIO ולתיאור"""
    try:
        img_captioner = ImageCaptioning()
        return img_captioner.process_bytesio_image(BytesIO(image_data.getvalue()), format=Image.open(BytesIO(image_data.getvalue())).format or 'PNG')
    except Exception as e:
        st.error(f"שגיאה בעיבוד תמונה: {e}")
        return None, None

def load_styles():
    """טעינת סגנונות"""
    try:
        with open('data/image_styles.json', 'r', encoding='utf-8') as f:
            return sorted(json.load(f).get('styles', []), key=lambda x: x.get('popularity_rank', 999))
    except Exception as e:
        st.error(f"שגיאה בטעינת הסגנונות: {e}")
        return []

def load_sample_images():
    """טעינת תמונות לדוגמה"""
    examples_dir = "examples"
    images = []
    if os.path.exists(examples_dir):
        for filename in os.listdir(examples_dir):
            file_path = os.path.join(examples_dir, filename)
            try:
                with open(file_path, "rb") as img_file:
                    image_uri = f"data:image/{filename.split('.')[-1]};base64,{base64.b64encode(img_file.read()).decode()}"
                images.append(image_uri)
            except Exception:
                continue
    return images

def main():
    st.title("🎨 מחולל התמונות החכם")
    styles = load_styles()
    
    col1, col2 = st.columns([2, 3])
    with col1:
        st.subheader("📸 העלאת תמונה")
        uploaded_file = st.file_uploader("העלה תמונה", type=["jpg", "jpeg", "png", "gif", "webp"])
        enable = st.checkbox("Enable camera")
        camera_photo = st.camera_input("צלם תמונה", disabled=not enable)
        
        if uploaded_file or camera_photo:
            st.session_state.selected_image, st.session_state.image_description = process_image(uploaded_file or camera_photo)
    
        with st.expander("תמונות לדוגמה"):
            sample_images = load_sample_images()
            for img in sample_images:
                st.image(img, width=200)
                if st.button("בחר תמונה", key=img):
                    st.session_state.selected_image = img

    with col2:
        if st.session_state.selected_image:
            st.subheader("🖼️ התמונה שנבחרה")
            st.image(st.session_state.selected_image, use_container_width=True)
            
            st.subheader("✨ הגדרות עיבוד")
            prompt = st.text_area("תיאור התמונה", translate(st.session_state.image_description, 'iw'), height=100)
            style = st.selectbox("בחר סגנון", [s['name'] for s in styles], index=0)
            
            if st.button("🎨 צור תמונה חדשה", type="primary") and prompt:
                with st.spinner('מייצר תמונה...'):
                    full_prompt = f"{next(s['prompt_prefix'] for s in styles if s['name'] == style)} {translate(prompt, 'en')}"
                    generator = PollinationsGenerator()
                    st.session_state.generated_image = generator.generate_image(full_prompt, "turbo")
                    if st.session_state.generated_image:
                        st.success('התמונה נוצרה בהצלחה!')
                    else:
                        st.error('אירעה שגיאה ביצירת התמונה.')
    
    if st.session_state.generated_image:
        st.subheader("🖼️ התמונה שנוצרה")
        st.image(st.session_state.generated_image, use_container_width=True)
        
        st.subheader("📱 שיתוף התמונה")
        _, share_col2 = st.columns(2)
        
        with share_col2:
            phone = st.text_input("מספר טלפון לשליחה בוואטסאפ", placeholder="הכנס מספר טלפון (לדוגמה: 0501234567)")
            
            if st.button("📲 שלח בוואטסאפ"):
                if phone and phone.isdigit() and len(phone) >= 9:
                    try:
                        img_data = base64.b64decode(st.session_state.generated_image.split(',')[1])
                        whatsapp = WhatsAppSender()
                        success = whatsapp.send_image_from_bytesio(
                            phone=phone,
                            image_bytesio=BytesIO(img_data),
                            caption="תמונה שנוצרה באמצעות מחולל התמונות החכם"
                        )
                        
                        if success:
                            st.success(f"התמונה נשלחה בהצלחה למספר {phone}")
                        else:
                            st.error("שגיאה בשליחת התמונה")
                    except Exception as e:
                        st.error(f"שגיאה בשליחת התמונה: {e}")
                else:
                    st.error("אנא הכנס מספר טלפון תקין")
    
if __name__ == "__main__":
    main()
