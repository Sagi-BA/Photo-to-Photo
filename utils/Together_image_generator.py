try:
    from together import Together
    import base64
    from io import BytesIO
    from PIL import Image
except ModuleNotFoundError:
    raise ImportError("The required packages are not installed. Please install them using 'pip install together-ai pillow'")

class ImageGenerator:
    def __init__(self, model="black-forest-labs/FLUX.1-schnell-Free", width=1024, height=768, steps=1, n=1, response_format="b64_json"):
        """
        Initializes the ImageGenerator with default parameters.
        :param model: The model used for image generation.
        :param width: Width of the generated image.
        :param height: Height of the generated image.
        :param steps: Number of steps for the image generation.
        :param n: Number of images to generate.
        :param response_format: The format of the response (default is base64 JSON).
        """
        self.client = Together()
        self.model = model
        self.width = width
        self.height = height
        self.steps = steps
        self.n = n
        self.response_format = response_format

    def generate_image(self, prompt):
        """
        Generates an image based on the given prompt.
        :param prompt: The text prompt for generating the image.
        :return: A list of PIL Image objects.
        """
        if not prompt:
            raise ValueError("Prompt cannot be empty")

        response = self.client.images.generate(
            prompt=prompt,
            model=self.model,
            width=self.width,
            height=self.height,
            steps=self.steps,
            n=self.n,
            response_format=self.response_format
        )
        
        if response and response.data:
            images = []
            for img_data in response.data:
                image_bytes = base64.b64decode(img_data.b64_json)
                image = Image.open(BytesIO(image_bytes))
                images.append(image)
            return images
        return None

# Example usage
if __name__ == "__main__":
    generator = ImageGenerator()
    prompt = "A futuristic city with flying cars and neon lights"
    try:
        images = generator.generate_image(prompt)
        if images:
            images[0].show()  # Display the first image
            print("Image OK")
        else:
            print("No image generated.")
    except Exception as e:
        print(f"Error: {e}")
