import base64
import streamlit as st
import json
import os
from PIL import Image
import io
from pathlib import Path
import time
import requests
from io import BytesIO

# Import custom utilities
from utils.pollinations_generator import PollinationsGenerator
from utils.greenapi import WhatsAppSender
from utils.Hugging_Face_Transformer import ImageCaptioning
from deep_translator import GoogleTranslator

# Set page config
st.set_page_config(
    page_title="מחולל התמונות החכם",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
        .stButton>button {
            width: 100%;
            height: 3rem;
            font-size: 1.2rem;
            margin-top: 1rem;
        }
        .st-emotion-cache-1v0mbdj > img {
            width: 100%;
            max-width: 300px;
        }
        .upload-text {
            font-size: 1.2rem;
            text-align: center;
            margin: 1rem 0;
        }
        .style-selector {
            font-size: 1.1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None
if 'selected_image' not in st.session_state:
    st.session_state.selected_image = None
if 'image_description' not in st.session_state:
    st.session_state.image_description = ""

def translate(text, target='en'):
    try:
        translator = GoogleTranslator(source='auto', target=target)
        return translator.translate(text)
    except Exception as e:
        st.error(f"שגיאה בתרגום: {str(e)}")
        return text
    
def process_image(image_data, source_type='file'):
    """Process image data from various sources and return BytesIO and description"""
    try:
        image_captioner = ImageCaptioning()
        
        if source_type == 'file':
            # For uploaded files or camera
            image_bytes = BytesIO(image_data.getvalue())
        elif source_type == 'base64':
            # For base64 encoded images
            image_bytes = BytesIO(base64.b64decode(image_data.split(',')[1]))
        else:
            return None, None
            
        # Get image format
        img = Image.open(image_bytes)
        format = img.format or 'PNG'
        
        # Process the image using the ImageCaptioning class
        image_uri, description = image_captioner.process_bytesio_image(image_bytes, format=format)
        
        return image_uri, description
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None, None

def load_styles():
    """Load and sort image styles from JSON file"""
    try:
        if not os.path.exists('data/image_styles.json'):
            st.error('קובץ הסגנונות לא נמצא!')
            return []

        with open('data/image_styles.json', 'r', encoding='utf-8') as f:
            styles_data = json.load(f)
        
        if not styles_data or 'styles' not in styles_data:
            st.error('תוכן קובץ הסגנונות אינו תקין!')
            return []

        sorted_styles = sorted(styles_data['styles'], key=lambda x: x.get('popularity_rank', 999))
        return sorted_styles
        
    except Exception as e:
        st.error(f'שגיאה בטעינת קובץ הסגנונות: {str(e)}')
        return []

def load_sample_images():
    """Load sample images from the examples folder"""
    images = []
    examples_dir = "examples"
    
    try:
        if not os.path.exists(examples_dir):
            st.error("תיקיית הדוגמאות לא נמצאה!")
            return []

        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        
        for filename in os.listdir(examples_dir):
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in valid_extensions:
                file_path = os.path.join(examples_dir, filename)
                
                try:
                    with Image.open(file_path) as img:
                        width, height = img.size
                        
                        with open(file_path, "rb") as img_file:
                            bytes_data = img_file.read()
                            image_uri = f"data:image/{file_ext[1:]};base64,{base64.b64encode(bytes_data).decode()}"
                        
                        images.append({
                            "uri": image_uri,
                            "filename": filename,
                            "width": width,
                            "height": height
                        })
                except Exception as e:
                    st.warning(f"שגיאה בטעינת התמונה {filename}: {str(e)}")
                    continue
                    
        return sorted(images, key=lambda x: x['filename'])
        
    except Exception as e:
        st.error(f"שגיאה בטעינת תמונות הדוגמה: {str(e)}")
        return []
    
def main():
    st.title("🎨 מחולל התמונות החכם")
    
    styles = load_styles()
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("📸 העלאת תמונה")
        upload_option = st.radio(
            "בחר אפשרות:",
            ["העלאת תמונה", "צילום תמונה"],
            index=0,
            horizontal=True
        )
        
        if upload_option == "העלאת תמונה":
            uploaded_file = st.file_uploader("העלה תמונה", type=["jpg", "jpeg", "png", "gif", "webp"])
            if uploaded_file:
                image_uri, description = process_image(uploaded_file, 'file')
                if image_uri:
                    st.session_state.selected_image = image_uri
                    st.session_state.image_description = description
                
        elif upload_option == "צילום תמונה":
            camera_photo = st.camera_input("צלם תמונה")
            if camera_photo:
                image_uri, description = process_image(camera_photo, 'file')
                if image_uri:
                    st.session_state.selected_image = image_uri
                    st.session_state.image_description = description
        
        with st.expander("תמונות לדוגמה:"):
            sample_images = load_sample_images()
            images_per_row = 4
            for i in range(0, len(sample_images), images_per_row):
                cols = st.columns(images_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(sample_images):
                        image = sample_images[i + j]
                        with col:
                            st.image(image["uri"], width=200)
                            if st.button(f"בחר תמונה {i+j+1}", key=f"sample_{i+j}"):
                                image_uri, description = process_image(image["uri"], 'base64')
                                if image_uri:
                                    st.session_state.selected_image = image_uri
                                    st.session_state.image_description = description
    
    with col2:
        if st.session_state.selected_image:
            st.subheader("🖼️ התמונה שנבחרה")
            st.image(st.session_state.selected_image, use_container_width=True)
            
            st.subheader("✨ הגדרות עיבוד")
            
            st.session_state.image_description=translate(st.session_state.image_description, target='hebrew')            

            prompt = st.text_area(
                "תיאור התמונה",
                value=st.session_state.image_description,
                height=100,
                help="תאר את התמונה שברצונך ליצור"
            )
            
            style = st.selectbox(
                "בחר סגנון",
                options=[style['name'] for style in styles],
                index=0,
                format_func=lambda x: x,
                help="בחר את הסגנון הרצוי לתמונה החדשה"
            )
            
            selected_style = next((s for s in styles if s['name'] == style), None)
            # if selected_style:
            #     with st.expander("ℹ️ מידע על הסגנון הנבחר"):
            #         st.write(f"תחילית הפרומפט: `{selected_style['prompt_prefix']}`")

            if st.button("🎨 צור תמונה חדשה", type="primary"):
                if prompt:
                    with st.spinner('מייצר תמונה...'):
                        english_prompt=translate(prompt, target='en')
                        full_prompt = f"{selected_style['prompt_prefix']} {english_prompt}".strip()
                        
                        generator = PollinationsGenerator()
                        image_data_uri = generator.generate_image(full_prompt, "turbo")
                        
                        if image_data_uri:
                            st.session_state.generated_image = image_data_uri
                            st.success('התמונה נוצרה בהצלחה!')
                        else:
                            st.error('אירעה שגיאה ביצירת התמונה. נסה שנית.')
                else:
                    st.warning('אנא הכנס תיאור לתמונה')
    
    if st.session_state.generated_image:
        st.subheader("🖼️ התמונה שנוצרה")
        st.image(st.session_state.generated_image, use_container_width=True)
        
        st.subheader("📱 שיתוף התמונה")
        share_col1, share_col2 = st.columns(2)
        
        with share_col2:
            phone = st.text_input(
                "מספר טלפון לשליחה בוואטסאפ",
                placeholder="הכנס מספר טלפון (לדוגמה: 0501234567)"
            )
            
            if st.button("📲 שלח בוואטסאפ"):
                if phone and phone.isdigit() and len(phone) >= 9:
                    try:
                        # Convert base64 to BytesIO
                        img_data = base64.b64decode(st.session_state.generated_image.split(',')[1])
                        image_bytesio = BytesIO(img_data)
                        
                        whatsapp = WhatsAppSender()
                        success = whatsapp.send_image_from_bytesio(
                            phone=phone,
                            image_bytesio=image_bytesio,
                            caption="תמונה שנוצרה באמצעות מחולל התמונות החכם"
                        )
                        
                        if success:
                            st.success(f"התמונה נשלחה בהצלחה למספר {phone}")
                        else:
                            st.error("שגיאה בשליחת התמונה")
                    except Exception as e:
                        st.error(f"שגיאה בשליחת התמונה: {str(e)}")
                else:
                    st.error("אנא הכנס מספר טלפון תקין")

if __name__ == "__main__":
    main()