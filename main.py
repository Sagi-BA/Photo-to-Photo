import asyncio
import base64
import streamlit as st
import json
import os
from PIL import Image
from io import BytesIO
from utils.counter import increment_user_count, get_user_count
from utils.groq_image_captioner import GroqImageCaptioner
from utils.imgur_uploader import ImgurUploader
from utils.init import initialize
from utils.pollinations_generator import PollinationsGenerator
from utils.greenapi import WhatsAppSender
from utils.TelegramSender import TelegramSender
# from utils.Hugging_Face_Transformer import ImageCaptioning
from deep_translator import GoogleTranslator
from datetime import datetime, time
import pytz

# Cache heavy models and resources
# @st.cache_resource
# def load_image_captioner():
#     """Load the image captioning model once and cache it"""
#     # with st.spinner('טוען מודל זיהוי תמונות... (יכול לקחת כמה שניות בפעם הראשונה)'):
#         return ImageCaptioning()

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

@st.cache_resource
def load_imgur_uploader():
    """Initialize Imgur uploader once"""
    return ImgurUploader()

def upload_to_imgur(image_data, is_base64=False):
    """Upload image to Imgur and return the URL"""
    try:
        # with st.spinner('מעלה תמונה לשרת...'):
        uploader = load_imgur_uploader()
        if not is_base64:
            # If it's not already base64, convert it
            base64_image = base64.b64encode(image_data).decode()
        else:
            # If it's a base64 data URL, remove the prefix
            if ',' in image_data:
                base64_image = image_data.split(',')[1]
            else:
                base64_image = image_data
                
        image_url = uploader.upload_media_to_imgur(
            base64_image,
            "image",
            "AI Generated Image",
            "Generated by Image Generator App"
        )
        return image_url
    except Exception as e:
        st.error(f"שגיאה בהעלאת תמונה: {e}")
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
                image, description = result
                if description:
                    with st.spinner('מתרגם את התיאור...'):
                        translated_desc = translate(description, 'iw')
                        # Upload to Imgur
                        image_url = upload_to_imgur(image, is_base64=True)
                        return image_url, translated_desc
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

# Initialize session state
if 'state' not in st.session_state:
    st.session_state.state = {
        'counted': False,
    }
    
# Set page config for better mobile responsiveness
st.set_page_config(layout="wide", initial_sidebar_state="collapsed", page_title="מחולל התמונות החכ", page_icon="📷")

# Read the HTML template
with open("template.html", "r", encoding="utf-8") as file:
    html_template = file.read()

# הגדרת עיצוב הדף
# st.set_page_config(page_title="מחולל התמונות החכם", page_icon="🎨", layout="wide")

async def send_telegram_image(image_data: str, caption: str):
    """Helper function to send image to Telegram"""
    try:
        # Convert base64 string to bytes
        if ',' in image_data:  # If it's a data URL
            image_base64 = image_data.split(',')[1]
        else:
            image_base64 = image_data
            
        # Convert to bytes
        image_bytes = BytesIO(base64.b64decode(image_base64))
        
        # Create a new TelegramSender instance for each send
        telegram_sender = TelegramSender()
        if await telegram_sender.verify_bot_token():
            await telegram_sender.send_photo_bytes(image_bytes, caption=caption)
        else:
            raise Exception("Bot token verification failed")
    except Exception as e:
        print(f"Failed to send to Telegram: {str(e)}")
        raise
    finally:
        await telegram_sender.close_session()

async def send_whatsapp_image(image_bytes: BytesIO, caption: str):
    """Helper function to send image to WhatsApp"""
    try:
        # Create WhatsApp sender instance
        whatsapp_sender = WhatsAppSender()
        
        # Get WhatsApp phone number from environment variables
        whatsapp_phone = os.getenv("WHATSAPP_PHONE")
        if not whatsapp_phone:
            raise Exception("WhatsApp phone number not configured in environment variables")
            
        # Reset bytes position for WhatsApp
        image_bytes.seek(0)
        
        # Send to WhatsApp
        success = whatsapp_sender.send_image_from_bytesio(
            whatsapp_phone,
            image_bytes,
            caption=caption
        )
        
        if not success:
            raise Exception("Failed to send image via WhatsApp")
            
    except Exception as e:
        print(f"Failed to send to WhatsApp: {str(e)}")
        raise

def load_html_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        return f.read()

def hide_streamlit_header_footer():
    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            footer:after {
                content:'goodbye'; 
                visibility: visible;
                display: block;
                position: relative;
                padding: 5px;
                top: 2px;
            }
            header {visibility: hidden;}
            #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)

# # CSS מותאם אישית
# st.markdown("""
#     <style>
#         .stButton>button { width: 100%; height: 3rem; font-size: 1.2rem; margin-top: 1rem; }
#         .st-emotion-cache-1v0mbdj > img { width: 100%; max-width: 300px; }
#         .upload-text { font-size: 1.2rem; text-align: center; margin: 1rem 0; }
#     </style>
# """, unsafe_allow_html=True)

# איתחול session state
for key in ['generated_image', 'selected_image', 'image_description']:
    st.session_state.setdefault(key, None if key != 'image_description' else "")

async def main():
    with st.spinner('האפליקציה נטענת...'):
        footer_content = initialize()
        # st.title("🎨 מחולל התמונות החכם")
        hide_streamlit_header_footer()
        styles = load_styles()

        # Load and display the custom expander HTML
        expander_html = load_html_file('expander.html')
        st.markdown(expander_html, unsafe_allow_html=True)    
    
    col1, col2 = st.columns([2, 3])
    with col1:
        st.subheader("העלאת תמונה 📸")
        uploaded_file = st.file_uploader("לעלות תמונה", type=["jpg", "jpeg", "png", "gif", "webp"])
        enable = st.checkbox("להפעלת המצלמה יש לסמן")
        camera_photo = st.camera_input("לצלם תמונה", disabled=not enable)
        
        if uploaded_file or camera_photo:
            st.session_state.selected_image, st.session_state.image_description = process_image(uploaded_file or camera_photo)            
        
        with st.expander("ניתן להשתמש בתמונות לדוגמה:"):
            with st.spinner('אני טוען תמונות לדוגמה...'):
                sample_images = load_sample_images()
            for img in sample_images:
                st.image(img, width=200)
                if st.button("בחרו תמונה", key=img):
                    img_bytes = decode_base64_to_bytes(img)
                    st.session_state.selected_image, st.session_state.image_description = process_image(img_bytes)
                    if st.session_state.selected_image is None:
                        st.session_state.selected_image = img

    with col2:
        if st.session_state.selected_image:
            st.subheader("התמונה שנבחרה 🖼️")
            st.image(st.session_state.selected_image, use_container_width=True)
            
            # st.subheader("✨ הגדרות עיבוד")
            with st.spinner('אני קורא את תוכן התמונה...'):
                prompt = st.text_area("תיאור התמונה", translate(st.session_state.image_description, 'iw'), height=100)
            style = st.selectbox("נא בחרו את סגנון התמונה החדשה שאתם רוצים שאייצר לכם...", [s['name'] for s in styles], index=0)
            
            if st.button("✨ לחצו עליי ותגלו את הקסם ✨", type="primary") and prompt:                
                # Get the selected style data
                selected_style = next(s for s in styles if s['name'] == style)
                full_prompt = f"{selected_style['prompt_prefix']} {translate(prompt, 'en')}"
                
                with st.spinner('אני יוצר את הקסם... (זה יכול לקחת עד 10 שניות)'):
                    generator = load_pollinations_generator()
                    # Use the model specified in the style
                    model = selected_style.get('model', 'turbo')  # Default to 'turbo' if no model specified
                    print(f"Using model: {model}")
                    st.session_state.generated_image = generator.generate_image(full_prompt, model)
                    if st.session_state.generated_image:
                        st.success('יצרתי לכם תמונה חדשה מה אתם אומרים?')
                    else:
                        st.error('אירעה שגיאה ביצירת התמונה.')
    
    if st.session_state.generated_image:
        st.subheader("הקסם הושלם – הנה היצירה שלכם! 🎉")
        st.image(st.session_state.generated_image, use_container_width=True)
        
        # Create telegram message
        telegram_caption = f"New image generated\nPrompt: {prompt}\nStyle: {style}"
        try:
            await send_telegram_image(st.session_state.generated_image, telegram_caption)
        except Exception as e:
            print(f"Error sending to Telegram: {e}")  # Log error but don't show to user
        
        st.subheader("🖼️ יצרתם תמונה מהממת! עכשיו הזמן לשתף אותה עם האהובים עליכם 💌")
    
        phone = st.text_input("מספר טלפון לשליחה בוואטסאפ", placeholder="למי לשלוח את היצירה? ( טלפון לדוגמה: 0501234567)")
        
        if st.button("לשתף בוואטסאפ 📲"):
            if phone and phone.isdigit() and len(phone) >= 9:
                try:
                    with st.spinner("אני שולח את התמונה לוואטסאפ..."):
                        img_data = base64.b64decode(st.session_state.generated_image.split(',')[1])
                        whatsapp = load_whatsapp_sender()
                        success = whatsapp.send_image_from_bytesio(
                            phone=phone,
                            image_bytesio=BytesIO(img_data),
                            caption= """✨ יצירת אמנות ייחודית שנוצרה במיוחד עבורכם באמצעות מחולל התמונות החכם של שגיא בר-און! 🌟
                            התנסו בעצמכם בכתובת: https://sagi-photo-to-photo.streamlit.app/
                            אהבתם? שתפו את החוויה עם חברים ומשפחה – זה לגמרי בחינם! 🎉"""
                        )
                        
                        if success:
                            st.success(f"התמונה נשלחה בהצלחה למספר {phone}")
                        else:
                            st.error("שגיאה בשליחת התמונה")
                except Exception as e:
                    st.error(f"שגיאה בשליחת התמונה: {e}")
            else:
                st.error("אנא הכנס מספר טלפון תקין")

    # Display footer content
    st.markdown(footer_content, unsafe_allow_html=True)    

    # Display user count
    user_count = get_user_count(formatted=True)
    st.markdown(f"<p class='user-count' style='color: #4B0082;'>סה\"כ משתמשים: {user_count}</p>", unsafe_allow_html=True)

    # Display LAST_DATETIME_USE value
    last_datetime_use = os.getenv("LAST_DATETIME_USE")
    st.markdown(f"<p class='last-datetime-use'>משתמש אחרון נכנס ב {last_datetime_use}</p>", unsafe_allow_html=True)

    # Update LAST_DATETIME_USE on first user entry
    if 'initial_visit' not in st.session_state:
        st.session_state.initial_visit = True
        israel_time = datetime.now(pytz.timezone("Asia/Jerusalem"))
        formatted_time = israel_time.strftime("%d/%m/%Y %H:%M")
        os.environ['LAST_DATETIME_USE'] = formatted_time

if __name__ == "__main__":
    if 'counted' not in st.session_state:
        st.session_state.counted = True
        increment_user_count()
    
    asyncio.run(main())