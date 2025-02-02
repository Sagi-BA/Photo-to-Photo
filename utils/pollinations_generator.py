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
            
            # Set up the headers and parameters
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
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
                    response = requests.get(
                        url, 
                        headers=headers,
                        params=params,
                        timeout=30,  # 30 seconds timeout
                        stream=True   # Stream the response
                    )
                    
                    # response.raise_for_status()
                    
                    # Read the content
                    image_data = response.content
                    
                    
                    # Verify it's an image by trying to open it
                    # img = Image.open(io.BytesIO(image_data))
                    
                    
                    # Convert to base64
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    
                    
                    # Return as data URI
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
    
    # Test cases
    test_cases = [
        {
            "prompt": "A beautiful sunset over the ocean, photorealistic",
            "model": "turbo",
            "output": "sunset_test.jpg"
        },
        {
            "prompt": "A cute cat playing with yarn, cartoon style",
            "model": "flux",
            "output": "cat_test.jpg"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['prompt']}")
        try:
            # Generate image
            result = generator.generate_image(test['prompt'], test['model'])
            
            if result:
                # Save the test image
                img_data = base64.b64decode(result.split(',')[1])
                with open(test['output'], 'wb') as f:
                    f.write(img_data)
                print(f"✓ Success - saved as {test['output']}")
            else:
                print("✗ Failed to generate image")
                
        except Exception as e:
            print(f"✗ Error in test {i}: {e}")
            
if __name__ == "__main__":
    test()