import requests
from PIL import Image
import io
import sys, os
from urllib.parse import quote
import base64
import time

class PollinationsGenerator:
    def __init__(self):
        self.pollinations_url = "https://image.pollinations.ai/prompt/{prompt}"

    def clean_text(self, text):
        """Clean text from HTML tags and normalize line breaks"""
        if not text:
            return ""
        # Replace HTML line breaks with spaces
        text = text.replace('<br>', ' ').replace('<br/>', ' ').replace('<br />', ' ')
        # Replace multiple spaces with single space
        text = ' '.join(text.split())
        return text

    def generate_image(self, prompt, model_name="flux"):
        """
        Generate image and return as data URI
        Args:
            prompt (str): The text description for image generation
            model_name (str): Model to use (flux/turbo)
        Returns:
            str: Data URI of the generated image or None if failed
        """
        try:
            # Encode the prompt for URL
            encoded_prompt = quote(self.clean_text(prompt))
            
            # Set up the parameters
            params = {
                'model': model_name,
                'width': 1280,
                'height': 720,
                'seed': 10,
                'nologo': 'true',
                'enhance': 'true'
            }
            
            # Build the complete URL
            url = self.pollinations_url.format(prompt=encoded_prompt)
            
            print(f"Requesting pollinations_url from: {url}")
            # Make the request to Pollinations API with retry logic
            max_retries = 4
            retry_delay = 5  # seconds
            
            for attempt in range(max_retries):
                try:
                    # Simple GET request without any headers
                    response = requests.get(url, params=params, timeout=30)
                    
                    # If we got an image, encode and return it
                    if response.content:
                        image_base64 = base64.b64encode(response.content).decode('utf-8')
                        return f"data:image/jpeg;base64,{image_base64}"
                    
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        print(f"Attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        print(f"Failed after {max_retries} attempts: {e}")
                        return None
                        
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

def test():
    """Test the image generation"""
    generator = PollinationsGenerator()
    
    test_prompt = "A beautiful sunset over the ocean, photorealistic"
    result = generator.generate_image(test_prompt, "flux")
    
    if result:
        # Save the test image
        img_data = base64.b64decode(result.split(',')[1])
        with open('test_output.jpg', 'wb') as f:
            f.write(img_data)
        print("✓ Success - saved as test_output.jpg")
    else:
        print("✗ Failed to generate image")
            
if __name__ == "__main__":
    test()