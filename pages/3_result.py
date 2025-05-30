# pages/3_result.py sagi 23:00
import streamlit as st
import base64
from io import BytesIO
import asyncio
import json
from utils.greenapi import WhatsAppSender
from utils.TelegramSender import TelegramSender
from utils.pollinations_generator import PollinationsGenerator
from deep_translator import GoogleTranslator
from utils.shared_styles import apply_styles
import re

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

async def send_telegram_image(image_data: str, caption: str):
    """Send image to Telegram"""
    try:
        if ',' in image_data:
            image_base64 = image_data.split(',')[1]
        else:
            image_base64 = image_data
        
        image_bytes = BytesIO(base64.b64decode(image_base64))
        telegram_sender = TelegramSender()
        
        if await telegram_sender.verify_bot_token():
            await telegram_sender.send_photo_bytes(image_bytes, caption=caption)
        else:
            raise Exception("Bot token verification failed")
    except Exception as e:
        print(f"Failed to send to Telegram: {str(e)}")
    finally:
        await telegram_sender.close_session()

@st.cache_resource
def load_whatsapp_sender():
    """Initialize WhatsApp sender once"""
    return WhatsAppSender()

def style_section():
    """Create the style selection section"""
    st.markdown("""
    <div class="custom-section style-section">
        <h3 style='color: #1e88e5; margin-bottom: 15px;' class="title-animation">✨ רוצים לנסות סגנון חדש? ✨</h3>
    </div>
    """, unsafe_allow_html=True)
    
    styles = load_styles()
    new_style = st.selectbox(
        "בחרו סגנון חדש לתמונה שלכם",
        [s['name'] for s in styles],
        index=0
    )
    
    regenerate = st.button("✨ צרו תמונה בסגנון חדש ✨", type="primary")
    return new_style, regenerate, styles

def whatsapp_section():
    """Create the WhatsApp sharing section"""
    st.markdown("""
    <div class="custom-section whatsapp-section">
        <h3 style='color: #2e7d32; margin-bottom: 15px;' class="title-animation">📱 שתפו את היצירה שלכם בוואטסאפ 📱</h3>
    </div>
    """, unsafe_allow_html=True)
    
    phone = st.text_input(
        "מספר טלפון לשליחה בוואטסאפ",
        placeholder="למי לשלוח את היצירה? (טלפון לדוגמה: 0501234567)"
    )
    
    share = st.button("📲 שלח בוואטסאפ 📲", type="primary")
    return phone, share

async def main_async():
    # apply_styles()
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
    
    # Check if we should be on this page
    if not st.session_state.state.get('image_processed'):
        st.session_state.state['current_page'] = '2_process'
        st.rerun()
        return

    # Track if we're generating a new image
    if 'is_generating' not in st.session_state:
        st.session_state.is_generating = False
        st.session_state.show_snow = True
    
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

    # Display title and image
    st.markdown("""
    <div class='custom-section'>
        <h2 style='color: #1e88e5; text-align: center; margin: 0;'>✨ הקסם הושלם – הנה היצירה שלכם! ✨</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.get("generated_image") and st.session_state.generated_image not in [None, ""]:
        def display_base64_image(data_uri):
            match = re.match(r"data:image/[^;]+;base64,(.*)", data_uri)
            if match:
                img_bytes = base64.b64decode(match.group(1))
                st.image(BytesIO(img_bytes))
            else:
                st.image(data_uri)

        display_base64_image(st.session_state.generated_image)
    else:
        st.warning("לא נמצאה תמונה להצגה (No image found to display)")
    
    # Only show snow if we're not generating and it's allowed
    if not st.session_state.is_generating and st.session_state.show_snow:
        st.snow()
        # Disable snow until next successful generation
        st.session_state.show_snow = False

    # Style selection section
    st.markdown("""
    <div class='custom-section'>
        <h3 style='color: #1e88e5; text-align: center; margin: 0;'>✨ רוצים לנסות סגנון חדש? ✨</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Load styles and create button grid
    styles = load_styles()
    cols = st.columns(2)
    
    for idx, style in enumerate(styles):
        with cols[idx % 2]:
            if st.button(
                f"{style['name']}",
                key=f"style_{idx}",
            ):
                st.session_state.is_generating = True
                st.session_state.show_snow = False
                
                # with st.spinner('✨ אני יוצר את הקסם... (זה יכול לקחת עד 30 שניות)'):
                with st.toast('אני יוצר את הקסם... (זה יכול לקחת עד 30 שניות)... המתינו עד שתראו ❄️❄️❄️'):
                    generator = PollinationsGenerator()
                    model = style.get('model', 'flux')
                    full_prompt = f"{style['prompt_prefix']} {translate(st.session_state.prompt, 'en')}"
                    
                    new_image = generator.generate_image(full_prompt, model)
                    if new_image:
                        st.session_state.generated_image = new_image
                        st.session_state.selected_style = style['name']
                        st.session_state.is_generating = False
                        st.session_state.show_snow = True  # Enable snow for next display
                        
                        # Send to Telegram
                        telegram_caption = f"New image generated\nPrompt: {st.session_state.prompt}\nStyle: {st.session_state.selected_style}"
                        try:
                            await send_telegram_image(new_image, telegram_caption)
                        except Exception as e:
                            print(f"Error sending to Telegram: {e}")
                        st.rerun()
                    else:
                        st.session_state.is_generating = False
                        st.error('אירעה שגיאה ביצירת התמונה - נסו שוב.')

    # WhatsApp sharing section
    # st.markdown("""
    # <div class='custom-section'>
    #     <h3 style='color: #2e7d32; text-align: center; margin: 0;'>📱 שתפו את היצירה שלכם בוואטסאפ 📱</h3>
    # </div>
    # """, unsafe_allow_html=True)
    
    phone = st.text_input(
        "מספר טלפון לשליחת התמונה בוואטסאפ",
        placeholder="למי לשלוח את היצירה? (טלפון לדוגמה: 0501234567)"
    )
    
    st.markdown('<div class="whatsapp-section">', unsafe_allow_html=True)
    if st.button("📲 שלחו בוואטסאפ 📲", type="primary"):
        if phone and phone.isdigit() and len(phone) >= 9:
            try:
                # with st.spinner("📱 שולח את התמונה בוואטסאפ..."):
                with st.spinner('אני שולח את ההודעה לוואטסאפ'):
                    img_data = base64.b64decode(st.session_state.generated_image.split(',')[1])
                    whatsapp = load_whatsapp_sender()
                    success = whatsapp.send_image_from_bytesio(
                        phone=phone,
                        image_bytesio=BytesIO(img_data),
                        caption="""✨ יצירת אמנות ייחודית שנוצרה במיוחד עבורכם באמצעות מחולל התמונות החכם של שגיא בר-און! 🌟
                        התנסו בעצמכם בכתובת: https://sagi-photo-to-photo.streamlit.app/
                        אהבתם? שתפו את החוויה עם חברים ומשפחה – זה לגמרי בחינם! 🎉"""
                    )
                    
                    if success:
                        st.success(f"✅ התמונה נשלחה בהצלחה למספר {phone}")
                    else:
                        st.error("❌ שגיאה בשליחת התמונה")
            except Exception as e:
                st.error(f"❌ שגיאה בשליחת התמונה: {e}")
        else:
            st.error("❌ אנא הכנס מספר טלפון תקין")
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
