import os
import time
import requests
from typing import Dict, Any, Tuple
from PIL import Image
import numpy as np
import tempfile
import io
import torch
import base64
from dotenv import load_dotenv

class SeedreamAPI:
    """Handles API calls to Seedream 4.0 service"""

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.api_key = os.getenv("ARK_API_KEY")
        if not self.api_key:
            raise ValueError("ARK_API_KEY not found in .env file")
        
        # Load model ID from environment variable
        self.default_model_id = os.getenv("MODEL_SEEDANCE_ID", "doubao-seedream-4-0-250828")

        self.base_url = os.getenv('ARK_API_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def encode_image_to_base64(self, image_data: bytes) -> str:
        """Encode image data to base64 string"""
        return base64.b64encode(image_data).decode('utf-8')

    def upload_image(self, image_data: bytes, filename: str) -> str:
        """Upload image and return URL"""
        upload_endpoint = f"{self.base_url}/files"
        files = {'file': (filename, image_data, 'image/png')}
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.post(upload_endpoint, headers=headers, files=files)
        response.raise_for_status()
        result = response.json()
        return result.get("url") or result.get("file_url")

    def image_to_base64_data_url(self, image_data: bytes, format: str = "png") -> str:
        """Convert image bytes to base64 data URL"""
        base64_str = self.encode_image_to_base64(image_data)
        return f"data:image/{format};base64,{base64_str}"

    def generate_image(self, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Submit image generation task"""
        endpoint = f"{self.base_url}/images/generations"

        # Get width and height from params
        width = params.get("width", 2048)
        height = params.get("height", 2048)

        # Create size string in "widthxheight" format
        size = f"{width}x{height}"

        payload = {
            "model": params.get("model", self.default_model_id),
            "prompt": prompt,
            "sequential_image_generation": params.get("sequential_image_generation", "disabled"),
            "response_format": "url",
            "size": size,
            "stream": False,
            "watermark": params.get("watermark", True)
        }

        # Add image data if provided (URLs or base64)
        if params.get("image_data"):
            payload["image"] = params["image_data"]

        # Add optional parameters
        if params.get("seed", 0) > 0:
            payload["seed"] = params["seed"]

        # Handle sequential image generation options
        if params.get("sequential_image_generation") == "auto":
            payload["sequential_image_generation_options"] = {
                "max_images": params.get("max_images", 1)
            }

        response = requests.post(endpoint, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def download_image(self, image_url: str) -> Image.Image:
        """Download image from URL"""
        response = requests.get(image_url)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))

class Seedream4Node:
    """ComfyUI node for Seedream 4.0 image generation"""

    @classmethod
    def INPUT_TYPES(cls):
        # Load default model ID from environment variable
        load_dotenv()
        default_model = os.getenv("MODEL_SEEDANCE_ID", "doubao-seedream-4-0-250828")
        
        return {
            "required": {
                "model": ([default_model],),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "Enter your image prompt"
                }),
                "size_preset": ([
                    "Custom",
                    "2048x2048 (1:1)",
                    "2304x1728 (4:3)",
                    "1728x2304 (3:4)",
                    "2560x1440 (16:9)",
                    "1440x2560 (9:16)",
                    "2496x1664 (3:2)",
                    "1664x2496 (2:3)",
                    "3024x1296 (21:9)",
                    "4096x4096 (1:1)"
                ], {
                    "default": "Custom"
                }),
                "width": ("INT", {
                    "default": 2048,
                    "min": 1280,
                    "max": 4096,
                    "step": 64
                }),
                "height": ("INT", {
                    "default": 2048,
                    "min": 720,
                    "max": 4096,
                    "step": 64
                }),
                "sequential_image_generation": (["disabled", "auto"], {
                    "default": "disabled"
                }),
                "max_images": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 15
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 2147483647
                }),
                "watermark": ("BOOLEAN", {
                    "default": True
                }),
                "image_encoding": (["url", "base64"], {
                    "default": "base64"
                })
            },
            "optional": {
                "input_images": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"
    CATEGORY = "BytePlus/Seedream"

    def generate(self, model: str, prompt: str, size_preset: str,
                width: int, height: int, sequential_image_generation: str, max_images: int, seed: int, watermark: bool, image_encoding: str, input_images=None):
        """Execute image generation"""

        if not prompt:
            raise ValueError("Prompt is required")

        # Apply size preset if not Custom
        if size_preset != "Custom":
            preset_sizes = {
                "2048x2048 (1:1)": (2048, 2048),
                "2304x1728 (4:3)": (2304, 1728),
                "1728x2304 (3:4)": (1728, 2304),
                "2560x1440 (16:9)": (2560, 1440),
                "1440x2560 (9:16)": (1440, 2560),
                "2496x1664 (3:2)": (2496, 1664),
                "1664x2496 (2:3)": (1664, 2496),
                "3024x1296 (21:9)": (3024, 1296),
                "4096x4096 (1:1)": (4096, 4096)
            }
            if size_preset in preset_sizes:
                width, height = preset_sizes[size_preset]

        # Initialize API client
        api = SeedreamAPI()

        # Handle input images if provided
        image_data = []
        input_image_count = 0
        if input_images is not None and sequential_image_generation == "auto":
            # Limit input images to ensure total doesn't exceed 15
            max_input_images = min(input_images.shape[0], 15 - max_images)

            if max_input_images <= 0:
                raise ValueError(f"max_images ({max_images}) is too large. Total images (input + generated) cannot exceed 15.")

            # Convert tensor images to PIL
            for i in range(max_input_images):
                img_tensor = input_images[i]
                img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
                pil_img = Image.fromarray(img_np)

                # Convert to bytes
                img_bytes = io.BytesIO()
                pil_img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                img_data = img_bytes.getvalue()

                try:
                    if image_encoding == "base64":
                        # Use base64 encoding
                        base64_data_url = api.image_to_base64_data_url(img_data, "png")
                        image_data.append(base64_data_url)
                    else:
                        # Upload image and get URL
                        image_url = api.upload_image(img_data, f"input_{i}.png")
                        image_data.append(image_url)
                    input_image_count += 1
                except Exception as e:
                    print(f"Warning: Failed to process image {i}: {e}")

            # Validate total image count
            total_images = input_image_count + max_images
            if total_images > 15:
                raise ValueError(f"Total images ({input_image_count} input + {max_images} generated = {total_images}) cannot exceed 15.")

        # Prepare parameters - pass width and height directly
        params = {
            "model": model,
            "width": width,
            "height": height,
            "sequential_image_generation": sequential_image_generation,
            "max_images": max_images,
            "seed": seed,
            "watermark": watermark,
            "image_data": image_data if image_data else None
        }

        try:
            # Submit generation task
            response = api.generate_image(prompt, params)

            # Handle direct response with URLs
            if "data" in response:
                images = []
                for item in response["data"]:
                    image_url = item.get("url")
                    if image_url:
                        pil_image = api.download_image(image_url)

                        # Convert PIL image to tensor (ComfyUI format)
                        img_array = np.array(pil_image).astype(np.float32) / 255.0
                        if len(img_array.shape) == 2:
                            img_array = np.expand_dims(img_array, axis=-1)
                            img_array = np.repeat(img_array, 3, axis=-1)
                        elif img_array.shape[-1] == 4:
                            img_array = img_array[:, :, :3]

                        images.append(img_array)

                if not images:
                    raise RuntimeError("No images generated")

                # Stack images into batch
                batch = torch.from_numpy(np.stack(images))
                return (batch,)
            else:
                raise RuntimeError("Invalid API response format")

        except Exception as e:
            raise RuntimeError(f"Seedream generation failed: {str(e)}")

class Seedream4ImageToImageNode:
    """ComfyUI node for Seedream 4.0 image-to-image generation"""

    @classmethod
    def INPUT_TYPES(cls):
        # Load default model ID from environment variable
        load_dotenv()
        default_model = os.getenv("MODEL_SEEDANCE_ID", "doubao-seedream-4-0-250828")
        
        return {
            "required": {
                "image": ("IMAGE",),
                "model": ([default_model],),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "Enter your image prompt"
                }),
                "strength": ("FLOAT", {
                    "default": 0.75,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 2147483647
                }),
                "watermark": ("BOOLEAN", {
                    "default": True
                })
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"
    CATEGORY = "BytePlus/Seedream"

    def generate(self, image, model: str, prompt: str,
                strength: float, seed: int, watermark: bool):
        """Execute image-to-image generation"""

        if not prompt:
            raise ValueError("Prompt is required")

        # Convert tensor to PIL image
        if isinstance(image, torch.Tensor):
            image_np = (image[0].cpu().numpy() * 255).astype(np.uint8)
            pil_image = Image.fromarray(image_np)
        else:
            raise ValueError("Invalid image format")

        # Save image to temporary file for upload
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            pil_image.save(tmp_file.name, "PNG")
            tmp_path = tmp_file.name

        try:
            # Initialize API client
            api = SeedreamAPI()

            # Note: The current API doesn't support image-to-image in the provided example
            # This would need to be implemented based on the actual img2img endpoint
            raise NotImplementedError("Image-to-image functionality not yet implemented for this API version")

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

NODE_CLASS_MAPPINGS = {
    "Seedream4": Seedream4Node,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Seedream4": "Seedream 4.0",
}