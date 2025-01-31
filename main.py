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

# Cache heavy models and resources
@st.cache_resource
def load_image_captioner():
    """Load the image captioning model once and cache it"""
    with st.spinner('טוען מודל זיהוי תמונות... (יכול לקחת כמה שניות בפעם הראשונה)'):
        return ImageCaptioning()

@st.cache_resource
def load_translator():
    """Initialize translator once"""
    return GoogleTranslator(source='auto', target='en')

@st.cache_resource
def load_whatsapp_sender():
    """Initialize WhatsApp sender once"""
    return WhatsAppSender()

@st.cache_resource
def load_pollinations_generator():
    """Initialize image generator once"""
    return PollinationsGenerator()

@st.cache_data
def load_styles():
    """טעינת סגנונות - cached for better performance"""
    try:
        with open('data/image_styles.json', 'r', encoding='utf-8') as f:
            styles = json.load(f).get('styles', [])
            # מיון הסגנונות לשתי קבוצות - סגנון חופשי ושאר הסגנונות
            free_style = [style for style in styles if style['name'] == "סגנון חופשי"]
            other_styles = [style for style in styles if style['name'] != "סגנון חופשי"]
            # מיון שאר הסגנונות לפי סדר אלפביתי
            sorted_other_styles = sorted(other_styles, key=lambda x: x['name'])
            # חיבור הרשימות - קודם סגנון חופשי ואחר כך שאר הסגנונות הממוינים
            return free_style + sorted_other_styles
    except Exception as e:
        st.error(f"שגיאה בטעינת הסגנונות: {e}")
        return []

@st.cache_data
def load_sample_images():
    """טעינת תמונות לדוגמה - cached for better performance"""
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

def translate(text, target='en'):
    """Translation using cached translator"""
    if not text:
        return ""
    try:
        translator = load_translator() if target == 'en' else GoogleTranslator(source='auto', target=target)
        return translator.translate(text)
    except Exception as e:
        st.error(f"שגיאה בתרגום: {e}")
        return text

def process_image(image_data):
    """עיבוד תמונה ל-BytesIO ולתיאור"""
    try:
        with st.spinner('מנתח את התמונה...'):
            img_captioner = load_image_captioner()
            
            if isinstance(image_data, BytesIO):
                image_bytesio = image_data
            else:
                image_bytesio = BytesIO(image_data.getvalue())
            
            img_format = Image.open(image_bytesio).format or 'PNG'
            image_bytesio.seek(0)
            
            result = img_captioner.process_bytesio_image(image_bytesio, format=img_format)
            if result and len(result) == 2:
                image, description = result
                if description:
                    with st.spinner('מתרגם את התיאור...'):
                        translated_desc = translate(description, 'iw')
                        return image, translated_desc
            return None, None
    except Exception as e:
        st.error(f"שגיאה בעיבוד תמונה: {e}")
        return None, None

def decode_base64_to_bytes(base64_string):
    """Convert base64 string to bytes for processing"""
    # Remove the data URL prefix if present
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    return BytesIO(base64.b64decode(base64_string))

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

def main():
    with st.spinner('טוען את האפליקציה...'):
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
            with st.spinner('טוען תמונות לדוגמה...'):
                sample_images = load_sample_images()
            for img in sample_images:
                st.image(img, width=200)
                if st.button("בחר תמונה", key=img):
                    img_bytes = decode_base64_to_bytes(img)
                    st.session_state.selected_image, st.session_state.image_description = process_image(img_bytes)
                    if st.session_state.selected_image is None:
                        st.session_state.selected_image = img

    with col2:
        if st.session_state.selected_image:
            st.subheader("🖼️ התמונה שנבחרה")
            st.image(st.session_state.selected_image, use_container_width=True)
            
            st.subheader("✨ הגדרות עיבוד")
            with st.spinner('מכין את התיאור...'):
                prompt = st.text_area("תיאור התמונה", translate(st.session_state.image_description, 'iw'), height=100)
            style = st.selectbox("בחר סגנון", [s['name'] for s in styles], index=0)
            
            if st.button("🎨 צור תמונה חדשה", type="primary") and prompt:
                with st.spinner('מתרגם את התיאור לאנגלית...'):
                    full_prompt = f"{next(s['prompt_prefix'] for s in styles if s['name'] == style)} {translate(prompt, 'en')}"
                
                with st.spinner('מייצר תמונה חדשה... (יכול לקחת עד 30 שניות)'):
                    generator = load_pollinations_generator()
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
                        with st.spinner('שולח את התמונה בוואטסאפ...'):
                            img_data = base64.b64decode(st.session_state.generated_image.split(',')[1])
                            whatsapp = load_whatsapp_sender()
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