import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import requests
from io import BytesIO
import base64

class ImageCaptioning:
    def __init__(self, model_name="Salesforce/blip-image-captioning-base"):
        """
        Initializes the ImageCaptioning class by loading the processor and model.
        Using base model instead of large for better performance.
        """
        torch.backends.cuda.matmul.allow_tf32 = True  # בשביל ביצועים טובים יותר
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        ).to(self.device)

    def describe_image(self, image_url):
        """
        Generates a textual description for the given image URL.
        """
        try:
            image = Image.open(requests.get(image_url, stream=True).raw).convert('RGB')
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                output = self.model.generate(**inputs, max_length=100)
            
            caption = self.processor.decode(output[0], skip_special_tokens=True)
            return caption
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return "Could not generate description"

    def process_bytesio_image(self, image_bytes: BytesIO, format: str = "PNG") -> tuple[str, str]:
        """
        Process an image from BytesIO and return its data URI and description.
        """
        try:
            # Reset BytesIO position
            image_bytes.seek(0)
            
            # Open and convert image
            img = Image.open(image_bytes).convert('RGB')
                
            # Generate description using BLIP model
            inputs = self.processor(images=img, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                output = self.model.generate(**inputs, max_length=100)
            description = self.processor.decode(output[0], skip_special_tokens=True)
            
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

# Test functionality
if __name__ == "__main__":
    captioner = ImageCaptioning()
    # Test with a sample image
    image_url = "http://images.cocodataset.org/val2017/000000039769.jpg"
    print("Testing image description...")
    description = captioner.describe_image(image_url)
    print(f"Description: {description}")