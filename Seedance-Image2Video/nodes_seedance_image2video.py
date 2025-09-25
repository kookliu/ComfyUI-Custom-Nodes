# -*- coding: utf-8 -*-
"""
Seedance Image-to-Video ComfyUI Node
Compatible with ComfyUI 0.3.59 and 0.4.x

- Reads API key from env: ARK_API_KEY
- Calls Seedance API to generate a video from image
- Uses download_url_to_video_output(...) to return a REAL VIDEO object
"""

import os
import time
import base64
import io
import requests
from typing import Dict, Any, Optional
from PIL import Image
import numpy as np

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# optional (only used by utils if available)
try:
    import folder_paths  # noqa: F401
    FOLDER_PATHS_AVAILABLE = True
except ImportError:
    FOLDER_PATHS_AVAILABLE = False

# ✅ 关键：使用相对导入（同目录内）
from .byteplus_video_utils import download_url_to_video_output, create_error_video_placeholder, download_url_to_image_output


def _extract_video_url_from_result(result: Dict[str, Any]) -> Optional[str]:
    """
    Try several common response shapes to find a video URL:
      1) {"content": {"video_url": "..."}}
      2) {"content": [{"type": "video", "video_url": "..."}]}
      3) {"output": {"video_url": "..."}}
      4) {"video_url": "..."}
    """
    content = result.get("content")
    if isinstance(content, dict) and "video_url" in content:
        return content["video_url"]
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("video_url"):
                return item["video_url"]

    output = result.get("output")
    if isinstance(output, dict) and "video_url" in output:
        return output["video_url"]

    if "video_url" in result:
        return result["video_url"]

    return None


def _extract_last_frame_url_from_result(result: Dict[str, Any]) -> Optional[str]:
    """从 API 响应中提取 last_frame_url"""
    if not result:
        return None
    
    # 检查 content 字段
    content = result.get('content')
    if not content:
        return None
    
    # 如果 content 是字典，直接查找 last_frame_url
    if isinstance(content, dict):
        return content.get('last_frame_url')
    
    # 如果 content 是列表，遍历查找
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and 'last_frame_url' in item:
                return item['last_frame_url']
    
    return None


def _image_to_base64(image_tensor) -> str:
    """
    Convert ComfyUI image tensor to base64 string
    image_tensor: torch tensor with shape [B, H, W, C] and values in [0, 1]
    """
    # Convert tensor to numpy array
    if hasattr(image_tensor, 'cpu'):
        image_np = image_tensor.cpu().numpy()
    else:
        image_np = np.array(image_tensor)

    # Handle batch dimension - take first image if batched
    if len(image_np.shape) == 4:
        # Shape is [B, H, W, C], take first image
        image_np = image_np[0]

    # Ensure we have [H, W, C] shape
    if len(image_np.shape) != 3:
        raise ValueError(f"Unexpected image shape: {image_np.shape}. Expected [H, W, C] or [B, H, W, C]")

    # Check the number of channels
    if image_np.shape[2] not in [3, 4]:
        raise ValueError(f"Unexpected number of channels: {image_np.shape[2]}. Expected 3 (RGB) or 4 (RGBA)")

    # Convert RGBA to RGB if necessary
    if image_np.shape[2] == 4:
        # Remove alpha channel
        image_np = image_np[:, :, :3]

    # Ensure values are in [0, 255] range
    if image_np.dtype == np.uint8:
        # Already in correct format
        pass
    elif image_np.max() <= 1.0:
        image_np = (image_np * 255).astype(np.uint8)
    else:
        image_np = np.clip(image_np, 0, 255).astype(np.uint8)

    # Convert to PIL Image - ensure it's RGB mode
    pil_image = Image.fromarray(image_np, mode='RGB')

    # Convert to base64
    buffer = io.BytesIO()
    pil_image.save(buffer, format='JPEG', quality=95)
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/jpeg;base64,{img_str}"


class SeedanceImage2VideoAPI:
    """Handles API calls to Seedance Image-to-Video service"""

    def __init__(self):
        if DOTENV_AVAILABLE:
            load_dotenv()

        self.api_key = os.getenv('ARK_API_KEY')
        if not self.api_key:
            raise ValueError("ARK_API_KEY environment variable is required")

        self.base_url = os.getenv('ARK_API_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def generate_video(self, image_tensor, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        # 从环境变量获取模型名称
        lite_model = os.getenv('SEEDANCE_LITE_T2V_MODEL', 'seedance-1-0-lite-i2v-250428')
        pro_model = os.getenv('SEEDANCE_PRO_MODEL', 'seedance-1-0-pro-250528')

        # 映射用户选择到实际模型名称
        model_mapping = {
            'seedance-1-0-lite-i2v-250428': lite_model,
            'seedance-1-0-pro-250528': pro_model,
            'doubao-seedance-1-0-lite-i2v-250428': lite_model,
            'doubao-seedance-1-0-pro-250528': pro_model,
        }
        actual_model = model_mapping.get(params.get('model'), lite_model)
        # Convert image to base64
        image_base64 = _image_to_base64(image_tensor)
        
        # Build text content with parameters
        text_content = prompt if prompt.strip() else "Generate a video from this image"
        if params.get('resolution'):
            text_content += f" --resolution {params['resolution']}"
        if params.get('aspect_ratio'):
            text_content += f" --ratio {params['aspect_ratio']}"
        if params.get('duration'):
            text_content += f" --duration {params['duration']}"
        if params.get('camera_fixed') is not None:
            text_content += f" --camerafixed {str(params['camera_fixed']).lower()}"
        if params.get('watermark') is not None:
            text_content += f" --watermark {str(params['watermark']).lower()}"
        if params.get('seed') is not None and params['seed'] != -1:
            text_content += f" --seed {params['seed']}"

        payload = {
            "model": actual_model,
            "return_last_frame": True,
            "content": [
                {"type": "text", "text": text_content},
                {"type": "image_url", "image_url": {"url": image_base64}}
            ],
        }

        r = requests.post(
            f"{self.base_url}/contents/generations/tasks",
            headers=self.headers,
            json=payload,
            timeout=60,
        )
        r.raise_for_status()
        return r.json()

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        r = requests.get(
            f"{self.base_url}/contents/generations/tasks/{task_id}",
            headers=self.headers,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def wait_for_completion(
        self,
        task_id: str,
        max_wait_time: int = 300,
        poll_interval: int = 5,
    ) -> Dict[str, Any]:
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            result = self.get_task_status(task_id)
            status = result.get("status", "unknown")
            
            if status == "succeeded":
                return result
            elif status == "failed":
                error_msg = result.get("error", {}).get("message", "Unknown error")
                raise RuntimeError(f"Video generation failed: {error_msg}")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Video generation timed out after {max_wait_time} seconds")


class SeedanceImage2VideoNode:
    """ComfyUI Node for Seedance Image-to-Video generation"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True, "default": "Generate a video from this image"}),
                "model": (["seedance-1-0-lite-i2v-250428", "seedance-1-0-pro-250528"], {"default": "seedance-1-0-lite-i2v-250428"}),
                "resolution": (["480p", "720p", "1080p"], {"default": "720p"}),
                "aspect_ratio": (["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"], {"default": "adaptive"}),
                "duration": ("INT", {"default": 5, "min": 3, "max": 12, "step": 1, "display": "slider"}),
                "seed": ("INT", {"default": 1, "min": -1, "max": 2147483647, "step": 1}),
                "camera_fixed": ("BOOLEAN", {"default": False}),
                "watermark": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("VIDEO", "IMAGE", "STRING")
    RETURN_NAMES = ("video", "last_frame", "response_info")
    FUNCTION = "generate"
    CATEGORY = "BytePlus/Seedance Image to Video"
    OUTPUT_NODE = True

    def _format_response_info(self, submit_resp: Dict[str, Any], done: Dict[str, Any],
                             video_url: str, last_frame_url: str) -> str:
        """格式化API响应信息为可读的字符串"""
        info_lines = [
            "=== Seedance Image2Video API 响应信息 ===",
            f"任务ID: {submit_resp.get('id', 'N/A')}",
            f"提交状态: {submit_resp.get('status', 'N/A')}",
            f"创建时间: {submit_resp.get('created_at', 'N/A')}",
            f"完成状态: {done.get('status', 'N/A')}",
            f"更新时间: {done.get('updated_at', 'N/A')}",
            f"视频URL: {video_url[:80] + '...' if len(video_url) > 80 else video_url}",
            f"最后一帧URL: {last_frame_url[:80] + '...' if last_frame_url and len(last_frame_url) > 80 else last_frame_url or 'N/A'}",
            "=== 完整API响应 ===",
            f"提交响应: {submit_resp}",
            f"完成响应: {done}",
        ]
        return "\n".join(info_lines)

    def generate(
        self,
        image,
        prompt: str,
        model: str,
        resolution: str,
        aspect_ratio: str,
        duration: int,
        seed: int,
        camera_fixed: bool,
        watermark: bool,
    ):
        try:
            api = SeedanceImage2VideoAPI()
            params = {
                'model': model,
                'resolution': resolution,
                'aspect_ratio': aspect_ratio,
                'duration': duration,  # Already integer from INPUT_TYPES
                'seed': seed if seed != -1 else None,
                'camera_fixed': camera_fixed,
                'watermark': watermark,
            }
            
            # Start generation task
            print("[Seedance Image2Video] Submitting video generation task...")
            submit_resp = api.generate_video(image, prompt, params)

            # 增强的API响应信息输出
            print("=" * 60)
            print("[Seedance Image2Video] 📤 API提交响应详情:")
            print(f"  🆔 任务ID: {submit_resp.get('id', 'N/A')}")
            print(f"  📊 状态: {submit_resp.get('status', 'N/A')}")
            print(f"  🕐 创建时间: {submit_resp.get('created_at', 'N/A')}")
            print(f"  📝 完整响应: {submit_resp}")
            print("=" * 60)

            task_id = submit_resp.get("id")
            if not task_id:
                raise ValueError("No task ID returned from API")

            print(f"[Seedance Image2Video] Task ID: {task_id}")

            # Wait for completion
            print("[Seedance Image2Video] Waiting for video generation to complete...")
            done = api.wait_for_completion(task_id)

            # 增强的完成响应信息输出
            print("=" * 60)
            print("[Seedance Image2Video] ✅ 任务完成响应详情:")
            print(f"  🆔 任务ID: {done.get('id', 'N/A')}")
            print(f"  📊 最终状态: {done.get('status', 'N/A')}")
            print(f"  🕐 更新时间: {done.get('updated_at', 'N/A')}")
            print(f"  🎬 视频信息: {done.get('result', {})}")
            print(f"  📝 完整响应: {done}")
            print("=" * 60)
            video_url = _extract_video_url_from_result(done)
            
            if not video_url:
                raise ValueError("No video URL found in API response")
            
            print(f"[Seedance Image2Video] Video URL: {video_url}")
            
            # Extract last frame URL
            last_frame_url = _extract_last_frame_url_from_result(done)
            print(f"[Seedance Image2Video] Last frame URL: {last_frame_url}")
            
            # Download video and last frame
            video_obj = download_url_to_video_output(video_url)
            
            # Download last frame if available
            if last_frame_url:
                try:
                    last_frame_image = download_url_to_image_output(last_frame_url)
                    print(f"[Seedance Image2Video] Last frame downloaded successfully")
                except Exception as e:
                    print(f"[Seedance Image2Video] Failed to download last frame: {e}")
                    # Create empty image tensor as fallback
                    import torch
                    last_frame_image = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
            else:
                print(f"[Seedance Image2Video] No last frame URL found")
                # Create empty image tensor as fallback
                import torch
                last_frame_image = torch.zeros((1, 512, 512, 3), dtype=torch.float32)

            status = done.get("status", "unknown")

            # 生成响应信息摘要
            response_info = self._format_response_info(submit_resp, done, video_url, last_frame_url)

            # 最终结果摘要输出
            print("=" * 60)
            print("[Seedance Image2Video] 🎉 生成任务完成摘要:")
            print(f"  ✅ 状态: {status}")
            print(f"  🆔 任务ID: {task_id}")
            print(f"  🎬 视频URL: {video_url}")
            print(f"  🖼️  最后一帧URL: {last_frame_url}")
            print(f"  📊 返回值: (VIDEO对象, IMAGE对象, 'response_info')")
            print("=" * 60)

            return (video_obj, last_frame_image, response_info)
            
        except Exception as e:
            error_msg = f"Seedance Image2Video generation failed: {str(e)}"
            print(f"[ERROR] {error_msg}")

            # Try to extract image dimensions for placeholder
            try:
                if hasattr(image, 'shape'):
                    if len(image.shape) == 4:
                        # [B, H, W, C]
                        height, width = image.shape[1], image.shape[2]
                    else:
                        # [H, W, C]
                        height, width = image.shape[0], image.shape[1]
                else:
                    # Default dimensions
                    height, width = 512, 512
            except:
                height, width = 512, 512

            # Always create error placeholder video (no longer returns None)
            placeholder_video = create_error_video_placeholder(width=width, height=height)
            
            # Create empty image tensor for last frame
            import torch
            empty_last_frame = torch.zeros((1, height, width, 3), dtype=torch.float32)

            # 错误情况下的响应信息
            from datetime import datetime
            error_response_info = f"=== Seedance Image2Video API 错误信息 ===\n错误: {str(e)}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            return (placeholder_video, empty_last_frame, error_response_info)


NODE_CLASS_MAPPINGS = {
    "SeedanceImage2Video": SeedanceImage2VideoNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SeedanceImage2Video": "ByteDance Image to Video",
}