# pages/1_upload.py
import streamlit as st
from utils.groq_image_captioner import GroqImageCaptioner
from utils.imgur_uploader import ImgurUploader
import base64
from io import BytesIO
from PIL import Image
import os
from utils.shared_styles import apply_styles

def clean_text(text):
    """Clean text from HTML tags and normalize line breaks"""
    if not text:
        return ""
    # Replace HTML line breaks with spaces
    text = text.replace('<br>', ' ').replace('<br/>', ' ').replace('<br />', ' ')
    # Replace multiple spaces with single space
    text = ' '.join(text.split())
    return text

def load_sample_images():
    """Load sample images from examples directory"""
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

def decode_base64_to_bytes(base64_string):
    """Convert base64 string to bytes"""
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    return BytesIO(base64.b64decode(base64_string))

def process_image(image_data):
    """עיבוד תמונה ל-BytesIO ולתיאור"""
    try:
        with st.spinner('אני מנתח את התמונה...'):
            captioner = GroqImageCaptioner()
            
            if isinstance(image_data, BytesIO):
                image_bytesio = image_data
            else:
                image_bytesio = BytesIO(image_data.getvalue())
            
            img_format = Image.open(image_bytesio).format or 'PNG'
            image_bytesio.seek(0)
            
            result = captioner.process_bytesio_image(image_bytesio, format=img_format)
            if result and len(result) == 2:
                base64_image, description = result
                if description:
                    # Upload to Imgur if it's a base64 image
                    if base64_image.startswith('data:image'):
                        try:
                            with st.spinner('מעלה תמונה לשרת...'):
                                uploader = ImgurUploader()
                                # Extract the base64 part without the prefix
                                base64_str = base64_image.split(',')[1]
                                image_url = uploader.upload_media_to_imgur(
                                    base64_str,
                                    "image",
                                    "AI Generated Image",
                                    "Generated by Image Generator App"
                                )
                                print(f"Image uploaded to Imgur: {image_url}")
                                return image_url, description
                        except Exception as e:
                            st.error(f"שגיאה בהעלאת תמונה לשרת: {e}")
                            return None, None
                    else:
                        return base64_image, description
            return None, None
    except Exception as e:
        st.error(f"שגיאה בעיבוד תמונה: {e}")
        return None, None

def process_and_navigate(image_data, is_sample=False):
    """Process image and navigate to next page"""
    if is_sample:
        img_bytes = decode_base64_to_bytes(image_data)
        image, description = process_image(img_bytes)
        if image:
            st.session_state.selected_image = image
            st.session_state.image_description = clean_text(description)
        else:
            st.session_state.selected_image = image_data
    else:
        image, description = process_image(image_data)
        if image:
            st.session_state.selected_image = image
            st.session_state.image_description = clean_text(description)
            
    # Set state and navigate to next page
    st.session_state.state['image_uploaded'] = True
    st.session_state.state['current_page'] = '2_process'
    st.rerun()

def main():
    # Apply shared styles
    apply_styles()
    
    st.subheader("העלאת תמונה 📸")
    
    # Create image source selector
    image_source = st.radio(
        "בחרו את מקור התמונה:",
        options=["העלאת תמונה", "צילום מהמצלמה", "בחירה מתמונות לדוגמה"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if image_source == "העלאת תמונה":
        uploaded_file = st.file_uploader("גררו לכאן תמונה או לחצו לבחירה", type=["jpg", "jpeg", "png", "gif", "webp"])
        if uploaded_file:
            process_and_navigate(uploaded_file)
    
    elif image_source == "צילום מהמצלמה":
        camera_photo = st.camera_input("צלמו תמונה")
        if camera_photo:
            process_and_navigate(camera_photo)
    
    else:  # Sample images
        with st.spinner('אני טוען תמונות לדוגמה...'):
            sample_images = load_sample_images()
            cols = st.columns(2)
            for idx, img in enumerate(sample_images):
                with cols[idx % 2]:
                    st.image(img, use_container_width=True)
                    if st.button("בחרו תמונה זו", key=f"sample_{idx}"):
                        process_and_navigate(img, is_sample=True)

if __name__ == "__main__":
    main()