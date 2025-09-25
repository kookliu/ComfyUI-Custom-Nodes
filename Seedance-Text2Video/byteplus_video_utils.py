# -*- coding: utf-8 -*-
# Utility helpers to convert a remote video URL into a REAL Comfy VIDEO object.
# Compatible with ComfyUI 0.3.59 and 0.4.x

import os
import time
import tempfile
import requests
from PIL import Image
import numpy as np
import torch

try:
    import folder_paths
    FOLDER_PATHS_AVAILABLE = True
except ImportError:
    FOLDER_PATHS_AVAILABLE = False


def _ensure_output_dir(default_subdir: str = "seedance_videos") -> str:
    if FOLDER_PATHS_AVAILABLE:
        base = folder_paths.get_output_directory()
        out = os.path.join(base, default_subdir)
    else:
        out = os.path.join(tempfile.gettempdir(), default_subdir)
    os.makedirs(out, exist_ok=True)
    return out


def _make_comfy_video_from_path(video_path: str):
    """
    Construct a REAL ComfyUI Video object from a file path.
    Compatible with ComfyUI 0.3.59 and newer versions.
    """
    errors = []

    # Method 1: Try VideoFromFile from comfy_api (ComfyUI 0.3.59+)
    try:
        from comfy_api.input_impl import VideoFromFile
        return VideoFromFile(video_path)
    except Exception as e:
        errors.append(f"comfy_api.input_impl.VideoFromFile -> {repr(e)}")

    # Method 2: Try alternative VideoFromFile import
    try:
        from comfy_api.latest.input_impl import VideoFromFile
        return VideoFromFile(video_path)
    except Exception as e:
        errors.append(f"comfy_api.latest.input_impl.VideoFromFile -> {repr(e)}")

    # Method 3: Try io.VideoInput
    try:
        import comfy_api.latest._io as io
        return io.VideoInput(video_path)
    except Exception as e:
        errors.append(f"comfy_api.latest._io.VideoInput -> {repr(e)}")

    # Method 4: Try direct io import
    try:
        import comfy_api.io as io
        return io.VideoInput(video_path)
    except Exception as e:
        errors.append(f"comfy_api.io.VideoInput -> {repr(e)}")

    # Method 5: Fallback - create a simple wrapper that mimics video object
    try:
        import cv2

        class SimpleVideoWrapper:
            def __init__(self, path):
                self.path = path
                # Get video dimensions
                cap = cv2.VideoCapture(path)
                self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()

            def get_dimensions(self):
                return self.width, self.height

            def save_to(self, output_path, format=None, codec=None, metadata=None):
                import shutil
                shutil.copy2(self.path, output_path)
                return output_path

        return SimpleVideoWrapper(video_path)
    except Exception as e:
        errors.append(f"SimpleVideoWrapper fallback -> {repr(e)}")

    raise RuntimeError(
        "Failed to create a ComfyUI Video object from path.\n" + "\n".join(errors)
    )


def download_url_to_video_output(
    video_url: str,
    timeout: int | None = 300,
    subdir: str = "seedance_videos",
    filename_prefix: str = "seedance_",
):
    """
    Download a remote video URL to mp4, then return a REAL Comfy VIDEO object.
    """
    out_dir = _ensure_output_dir(subdir)
    ts = int(time.time())
    video_path = os.path.join(out_dir, f"{filename_prefix}{ts}.mp4")

    with requests.get(video_url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        with open(video_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    print(f"[Seedance] Video saved to: {video_path}")
    return _make_comfy_video_from_path(video_path)


def create_empty_video_object(width: int = 512, height: int = 512, duration_seconds: float = 1.0, fps: int = 24):
    """
    Create an empty/dummy video object for error handling.
    Returns a video object that can be used when API calls fail.
    """
    try:
        import cv2
        import tempfile
        
        # Create a temporary black video file
        out_dir = _ensure_output_dir("temp_videos")
        ts = int(time.time())
        temp_video_path = os.path.join(out_dir, f"empty_video_{ts}.mp4")
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))
        
        # Write black frames
        total_frames = int(duration_seconds * fps)
        black_frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        for _ in range(total_frames):
            out.write(black_frame)
        
        out.release()
        
        # Return ComfyUI video object
        return _make_comfy_video_from_path(temp_video_path)
        
    except Exception as e:
        print(f"[Seedance] Warning: Failed to create empty video object: {e}")
        # Return a simple wrapper as last resort
        class EmptyVideoWrapper:
            def __init__(self):
                self.width = width
                self.height = height
                
            def get_dimensions(self):
                return self.width, self.height
                
            def save_to(self, output_path, format=None, codec=None, metadata=None):
                # Create a minimal empty video file
                try:
                    import cv2
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(output_path, fourcc, 1, (self.width, self.height))
                    black_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                    out.write(black_frame)
                    out.release()
                    return output_path
                except:
                    # If even this fails, just create an empty file
                    with open(output_path, 'w') as f:
                        f.write("")
                    return output_path
        
        return EmptyVideoWrapper()


def download_url_to_image_output(
    image_url: str,
    timeout: int | None = 300,
    subdir: str = "seedance_images",
    filename_prefix: str = "seedance_frame_",
):
    """
    Download a remote image URL and return a ComfyUI IMAGE tensor.
    ComfyUI IMAGE format: torch.Tensor with shape [batch, height, width, channels]
    Values should be in range [0, 1] and dtype float32.
    """
    out_dir = _ensure_output_dir(subdir)
    ts = int(time.time())
    image_path = os.path.join(out_dir, f"{filename_prefix}{ts}.jpg")

    # Download the image
    with requests.get(image_url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        with open(image_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    print(f"[Seedance] Image saved to: {image_path}")
    
    # Load image with PIL and convert to ComfyUI format
    pil_image = Image.open(image_path)
    
    # Convert to RGB if necessary
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    
    # Convert PIL image to numpy array
    np_image = np.array(pil_image).astype(np.float32) / 255.0
    
    # Convert to torch tensor and add batch dimension
    # ComfyUI expects [batch, height, width, channels]
    torch_image = torch.from_numpy(np_image).unsqueeze(0)
    
    return torch_image
