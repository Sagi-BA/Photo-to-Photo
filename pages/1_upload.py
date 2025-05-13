# pages/1_upload.py
import streamlit as st
from utils.groq_image_captioner import GroqImageCaptioner
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

def convert_to_base64(image_data):
    """Convert image data to base64 data URI"""
    try:
        if isinstance(image_data, BytesIO):
            image_bytes = image_data.getvalue()
        else:
            image_bytes = image_data.getvalue()
            
        # Get image format
        image = Image.open(BytesIO(image_bytes))
        img_format = image.format.lower() if image.format else 'jpeg'
        
        # Convert to base64
        base64_str = base64.b64encode(image_bytes).decode()
        return f"data:image/{img_format};base64,{base64_str}"
    except Exception as e:
        st.error(f"שגיאה בהמרת תמונה: {e}")
        return None

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
                    # If it's already a base64 image, return it directly
                    if base64_image.startswith('data:image'):
                        return base64_image, description
                    # Otherwise convert to base64
                    image_base64 = convert_to_base64(image_bytesio)
                    return image_base64, description
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
    # apply_styles()
    
    st.subheader("העלאת תמונה 📸")
    
    # Create image source selector
    image_source = st.radio(
        "בחרו את מקור התמונה:",
        options=["העלאת תמונה", "צילום מהמצלמה", "בחירה מתמונות לדוגמה"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if image_source == "העלאת תמונה":
        uploaded_file = st.file_uploader(
            "גררו לכאן תמונה או לחצו לבחירה",  # Hebrew text for "Drag and drop file here or click"
            type=["jpg", "jpeg", "png", "gif", "webp"],
            label_visibility='collapsed',  # This hides the label above
            help="JPG, JPEG, PNG, GIF, WEBP קבצים עד 5MB מסוג"  # Hebrew text for file types
        )
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
                    st.image(img)
                    if st.button("בחרו תמונה זו", key=f"sample_{idx}"):
                        process_and_navigate(img, is_sample=True)

if __name__ == "__main__":
    main()