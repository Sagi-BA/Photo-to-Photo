# 🎨 מחולל התמונות החכם | Smart Image Generator

An AI-powered image generation and analysis app with multi-model support and smart style selection.

> Try the app [here](https://sagi-photo-to-photo.streamlit.app/)

[![Linktree](https://img.shields.io/badge/linktree-white?style=for-the-badge&logo=linktree&logoColor=43E55E)](https://linktr.ee/sagib?lt_utm_source=lt_share_link#373198503) |
[![Facebook](https://img.shields.io/badge/facebook-white?style=for-the-badge&logo=facebook&logoColor=0866FF)](https://www.facebook.com/sagi.baron) |
[![LinkedIn](https://img.shields.io/badge/linkedin-white?style=for-the-badge&logo=linkedin&logoColor=0A66C2)](https://www.linkedin.com/in/sagi-bar-on) |
[![Contact Me](https://img.shields.io/badge/CONTACT_ME-white?style=for-the-badge&logo=whatsapp&logoColor=25D366)](https://api.whatsapp.com/send?phone=972549995050) |
[![AI Tips & Tricks Channel](https://img.shields.io/badge/AI_TIPS_&_TRICKS_CHANNEL-white?style=for-the-badge&logo=whatsapp&logoColor=25D366)](https://whatsapp.com/channel/0029Vaj33VkEawds11JP9o1c) |
[![AI Discussion Group](https://img.shields.io/badge/AI_DISCUSSION_GROUP-white?style=for-the-badge&logo=whatsapp&logoColor=25D366)](https://whatsapp.com/channel/0029Vaj33VkEawds11JP9o1c) |
[![Subscribe](https://img.shields.io/badge/Subscribe_to_my_YouTube_channel-white?style=for-the-badge&logo=youtube&logoColor=FF0000)](https://www.youtube.com/@SagiBaron) |
[![Ask New AI Video](https://img.shields.io/badge/Ask_For_New_AI_Video-white?style=for-the-badge&logo=GoogleForms&logoColor=7248B9)](https://forms.gle/b5hw4Rfe6ZtXuiQV6) |
[![Email Me](https://img.shields.io/badge/email_me-white?style=for-the-badge&logo=gmail&logoColor=EA4335)](mailto:sagi.baron76@gmail.com) |
[![Buy Me A Beer](https://img.shields.io/badge/Buy_Me_A_Beer-white?style=for-the-badge&logo=buymeacoffee&logoColor=FFDD00)](https://buymeacoffee.com/sagibar)

## 🌟 Features

- **Smart Image Analysis**: Uses Groq's LLaMA Vision model for detailed image descriptions
- **Multiple Art Styles**: Generate images in various styles including:
  - Abstract
  - Digital Art
  - Disney/Pixar Style
  - Anime
  - Photorealistic
  - And many more!
- **Multi-Model Support**: Different AI models optimized for each style
- **WhatsApp Integration**: Share generated images directly via WhatsApp
- **Imgur Integration**: Fast image loading and sharing
- **Bilingual Support**: Hebrew and English interfaces

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Image Generation**: Pollinations API with multiple models
- **Image Analysis**: Groq LLaMA Vision
- **Image Hosting**: Imgur API
- **Translation**: Google Translate API
- **Messaging**: WhatsApp API

## 🚀 Getting Started

### Prerequisites

Make sure you have Python 3.8+ installed on your system.

### Environment Setup

Create a `.env` file with your API keys:

```env
GROQ_API_KEY=your_groq_api_key
IMGUR_CLIENT_ID=your_imgur_client_id
GROQ_MODEL=llama-3.2-11b-vision-preview
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=1024
```

### Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd [your-repo-name]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run main.py
```

## 📱 Usage

1. **Upload or Take a Photo**: Use your camera or upload an image
2. **Get Description**: AI will analyze and describe the image in detail
3. **Choose Style**: Select from various artistic styles
4. **Generate New Image**: Create a new image based on the description and selected style
5. **Share**: Send the generated image via WhatsApp

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to Groq for their powerful LLaMA Vision model
- Thanks to Pollinations for their image generation API
- Thanks to all contributors and users of this project