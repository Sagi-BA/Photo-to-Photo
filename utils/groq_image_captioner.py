import base64
from groq import Groq
import os
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GroqImageCaptioner:
    def __init__(self, api_key=None):
        """Initialize the Groq client with API key and parameters from .env"""
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key not found. Please provide it or set GROQ_API_KEY environment variable.")
        
        # Load model parameters from .env with defaults
        self.model = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
        self.temperature = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("GROQ_MAX_TOKENS", "1024"))
        
        self.client = Groq(api_key=self.api_key)
        self.system_prompt = """You are describing an image to someone who is blind. Please be as detailed as possible.
1. Start with the overall subject or theme of the image in simple terms.
2. Describe the background: colors, patterns, or environmental details.
3. Describe the main subjects or objects in the image, including their position, appearance, clothing, expressions, textures, and actions.
4. Highlight the mood or atmosphere of the scene.
5. Mention any lighting effects, shadows, or other visual elements.
6. Be specific and avoid assumptions unless visually evident."""

    def _image_to_data_url(self, image_bytes: BytesIO, format: str = "PNG") -> str:
        """Convert image bytes to base64 data URL"""
        image_bytes.seek(0)
        base64_image = base64.b64encode(image_bytes.read()).decode()
        return f"data:image/{format.lower()};base64,{base64_image}"

    def process_bytesio_image(self, image_bytes: BytesIO, format: str = "PNG") -> tuple[str, str]:
        """
        Process an image from BytesIO and return its data URI and description.
        """
        try:
            # Convert image to data URL
            image_data_url = self._image_to_data_url(image_bytes, format)
            
            # Create completion request
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{self.system_prompt}\n\nDescribe the following image in detail:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_data_url
                                }
                            }
                        ]
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=1,
                stream=False
            )
            
            # Get description from response
            description = completion.choices[0].message.content
            
            # Return both the image data URL and description
            return image_data_url, description
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None, None

    def describe_image(self, image_url: str) -> str:
        """
        Generate a description for an image from a URL.
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{self.system_prompt}\n\nDescribe the following image in detail:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=1,
                stream=False
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Error describing image: {str(e)}")
            return "Could not generate description"

# Example .env file content:
"""
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.2-11b-vision-preview
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=1024
"""

# Test functionality
if __name__ == "__main__":
    captioner = GroqImageCaptioner()
    
    # Test with a sample image
    with open("test_image.jpg", "rb") as img_file:
        image_bytes = BytesIO(img_file.read())
        image_url, description = captioner.process_bytesio_image(image_bytes)
        print(f"Description: {description}")