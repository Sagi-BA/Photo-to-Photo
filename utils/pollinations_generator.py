import requests
from PIL import Image
import io
import sys, os
from urllib.parse import quote
import base64
import time
import logging

class PollinationsGenerator:
    def __init__(self):
        self.pollinations_url = "https://image.pollinations.ai/prompt/{prompt}"
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def clean_text(self, text):
        """Clean text from HTML tags and normalize line breaks"""
        if not text:
            return ""
        # Replace HTML line breaks with spaces
        text = text.replace('<br>', ' ').replace('<br/>', ' ').replace('<br />', ' ')
        # Replace multiple spaces with single space
        text = ' '.join(text.split())
        return text

    def is_valid_image(self, image_data):
        """Validate if the data is a proper image"""
        try:
            # Try to open the image data with PIL
            img = Image.open(io.BytesIO(image_data))
            img.verify()
            
            # Check image dimensions
            img = Image.open(io.BytesIO(image_data))  # Need to reopen after verify
            width, height = img.size
            
            # Check if image dimensions are reasonable (not too small)
            if width < 100 or height < 100:
                return False
                
            # Check if image isn't completely black or white
            if img.mode == 'RGB':
                extrema = img.getextrema()
                is_solid_color = all(min_val == max_val for min_val, max_val in extrema)
                if is_solid_color:
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"Image validation failed: {e}")
            return False

    def _save_image_to_file(self, image_data):
        """Save image data to a temporary file and return the filename"""
        try:
            timestamp = int(time.time())
            filename = f'temp_image_{timestamp}.jpg'
            
            # Ensure the image is in JPEG format
            img = Image.open(io.BytesIO(image_data))
            if img.mode in ('RGBA', 'LA'):
                # Convert RGBA to RGB for JPEG compatibility
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            # Save with optimized quality
            img.save(filename, 'JPEG', quality=95, optimize=True)
            self.logger.info(f"Image saved successfully to {filename}")
            
            # Read back the file and convert to base64
            with open(filename, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Clean up the temporary file
            os.remove(filename)
            return f"data:image/jpeg;base64,{image_base64}"
            
        except Exception as e:
            self.logger.error(f"Error in save_image_to_file: {e}")
            return None

    def generate_image(self, prompt, model_name="flux"):
        """
        Generate image and return as data URI with improved error handling
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
            self.logger.info(f"Requesting pollinations_url from: {url}")
            
            # Make the request to Pollinations API with retry logic
            max_retries = 4
            retry_delay = 5  # seconds
            wait_time = 2  # Initial wait time between request and validation
            
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, params=params, timeout=30)
                    
                    if response.status_code == 200:
                        time.sleep(wait_time)
                        
                        if response.content and self.is_valid_image(response.content):
                            try:
                                # First attempt: direct base64 encoding
                                image_base64 = base64.b64encode(response.content).decode('utf-8')
                                return f"data:image/jpeg;base64,{image_base64}"
                            except Exception as encode_error:
                                self.logger.warning(f"Direct base64 encoding failed: {encode_error}")
                                self.logger.info("Attempting file-based conversion...")
                                
                                # Second attempt: file-based approach
                                result = self._save_image_to_file(response.content)
                                if result:
                                    return result
                                
                                self.logger.error("Both conversion methods failed")
                                return None
                        else:
                            # If validation failed, increase wait time and retry
                            wait_time = min(wait_time * 1.5, 10)  # Max 10 seconds wait
                            if attempt < max_retries - 1:
                                continue
                            
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        self.logger.error(f"Failed after {max_retries} attempts: {e}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Unexpected error in generate_image: {e}")
            return None

def test():
    """Test the image generation"""
    generator = PollinationsGenerator()
    
    test_prompt = "A beautiful sunset over the ocean, photorealistic"
    result = generator.generate_image(test_prompt, "flux")
    
    if result:
        # Test the base64 string validity
        try:
            # Extract the base64 part
            base64_str = result.split(',')[1]
            # Try to decode it
            decoded = base64.b64decode(base64_str)
            print("✓ Success - base64 encoding is valid")
            
            # Save test image
            with open('test_output.jpg', 'wb') as f:
                f.write(decoded)
            print("✓ Success - saved as test_output.jpg")
        except Exception as e:
            print(f"✗ Failed to validate base64 string: {e}")
    else:
        print("✗ Failed to generate image")
            
if __name__ == "__main__":
    test()