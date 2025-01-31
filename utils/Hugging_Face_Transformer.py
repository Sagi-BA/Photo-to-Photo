from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import requests
from io import BytesIO
import base64
import os

class ImageCaptioning:
    def __init__(self, model_name="Salesforce/blip-image-captioning-large"):
        """
        Initializes the ImageCaptioning class by loading the processor and model.
        :param model_name: The name of the pre-trained BLIP model.
        """
        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(model_name)

    def describe_image(self, image_url):
        """
        Generates a textual description for the given image URL.
        :param image_url: The URL of the image to be described.
        :return: The generated caption as a string.
        """
        try:
            image = Image.open(requests.get(image_url, stream=True).raw).convert("RGB")
            inputs = self.processor(images=image, return_tensors="pt")
            caption_ids = self.model.generate(**inputs)
            caption = self.processor.batch_decode(caption_ids, skip_special_tokens=True)[0]
            return caption
        except Exception as e:
            return f"Error processing image: {e}"

    def process_bytesio_image(self, image_bytes: BytesIO, format: str = "PNG") -> tuple[str, str]:
        """
        Process an image from BytesIO and return its data URI and description.
        
        Args:
            image_bytes (BytesIO): The image in BytesIO format
            format (str): The image format (default: "PNG")
        
        Returns:
            tuple[str, str]: (image_uri, description)
        """
        try:
            # Reset BytesIO position
            image_bytes.seek(0)
            
            # Open image with PIL
            img = Image.open(image_bytes)
            
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")
                
            # Generate description using BLIP model
            inputs = self.processor(images=img, return_tensors="pt")
            caption_ids = self.model.generate(**inputs)
            description = self.processor.batch_decode(caption_ids, skip_special_tokens=True)[0]
            
            # Save to a new BytesIO for the URI
            output_bytes = BytesIO()
            img.save(output_bytes, format=format)
            output_bytes.seek(0)
            
            # Convert to base64
            encoded_image = base64.b64encode(output_bytes.getvalue()).decode()
            image_uri = f"data:image/{format.lower()};base64,{encoded_image}"
            
            return image_uri, description
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None, None

# Example usage
if __name__ == "__main__":
    captioner = ImageCaptioning()
    
    # Test URL-based description
    image_url = "https://t4.ftcdn.net/jpg/05/01/84/43/360_F_501844341_cA5xxjYPd4hL19XMImLMj5sCnP1Ib4hI.jpg"
    description = captioner.describe_image(image_url)
    print("URL Image Description:", description)
    
    # Test BytesIO-based description
    try:
        # Create a test BytesIO image
        response = requests.get(image_url)
        image_bytes = BytesIO(response.content)
        
        image_uri, description = captioner.process_bytesio_image(image_bytes)
        print("\nBytesIO Image Description:", description)
        print("Image URI generated successfully:", bool(image_uri))
    except Exception as e:
        print(f"Error in BytesIO test: {e}")