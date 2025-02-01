# pages/3_🎨_result.py
import streamlit as st
import base64
from io import BytesIO
import asyncio
from utils.greenapi import WhatsAppSender
from utils.TelegramSender import TelegramSender

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

def share_on_whatsapp(phone, image_data):
    """Share image on WhatsApp"""
    try:
        with st.spinner("אני שולח את התמונה לוואטסאפ..."):
            img_data = base64.b64decode(image_data.split(',')[1])
            whatsapp = WhatsAppSender()
            success = whatsapp.send_image_from_bytesio(
                phone=phone,
                image_bytesio=BytesIO(img_data),
                caption="""✨ יצירת אמנות ייחודית שנוצרה במיוחד עבורכם באמצעות מחולל התמונות החכם של שגיא בר-און! 🌟
                התנסו בעצמכם בכתובת: https://sagi-photo-to-photo.streamlit.app/
                אהבתם? שתפו את החוויה עם חברים ומשפחה – זה לגמרי בחינם! 🎉"""
            )
            return success
    except Exception as e:
        st.error(f"שגיאה בשליחת התמונה: {e}")
        return False

@st.cache_resource
def load_whatsapp_sender():
    """Initialize WhatsApp sender once"""
    return WhatsAppSender()

async def main_async():
    # Check if we should be on this page
    if not st.session_state.state.get('image_processed'):
        st.session_state.state['current_page'] = '2_process'
        st.rerun()
        return
    
    # Display selected image
    body = "יצרתי לכם תמונה חדשה מה אתם אומרים"
    st.toast(body, icon='🎉')

    st.subheader("הקסם הושלם – הנה היצירה שלכם! 🎉")
    st.image(st.session_state.generated_image, use_container_width=True)
    st.snow()

    # Create telegram message
    telegram_caption = f"New image generated\nPrompt: {st.session_state.prompt}\nStyle: {st.session_state.selected_style}"
    try:
        await send_telegram_image(st.session_state.generated_image, telegram_caption)
    except Exception as e:
        print(f"Error sending to Telegram: {e}")  # Log error but don't show to user

    st.subheader("🖼️ יצרתם תמונה מהממת! עכשיו הזמן לשתף אותה עם האהובים עליכם 💌")
    
    phone = st.text_input("מספר טלפון לשליחה בוואטסאפ", placeholder="למי לשלוח את היצירה? ( טלפון לדוגמה: 0501234567)")
    
    if st.button("לחצו לשתף בוואטסאפ 📲"):
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

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()