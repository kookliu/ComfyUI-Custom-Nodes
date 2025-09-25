# -*- coding: utf-8 -*-
"""
Seedance Text-to-Video ComfyUI Node
Compatible with ComfyUI 0.3.59 and 0.4.x

- Reads API key from env: ARK_API_KEY
- Calls Seedance API to generate a video
- Uses download_url_to_video_output(...) to return a REAL VIDEO object
"""

import os
import time
import requests
from typing import Dict, Any, Optional

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
from .byteplus_video_utils import download_url_to_video_output, download_url_to_image_output, create_empty_video_object


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
    """
    Try several common response shapes to find a last_frame_url:
      1) {"content": {"last_frame_url": "..."}}
      2) {"content": [{"type": "image", "last_frame_url": "..."}]}
      3) {"output": {"last_frame_url": "..."}}
      4) {"last_frame_url": "..."}
    """
    content = result.get("content")
    if isinstance(content, dict) and "last_frame_url" in content:
        return content["last_frame_url"]
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("last_frame_url"):
                return item["last_frame_url"]

    output = result.get("output")
    if isinstance(output, dict) and "last_frame_url" in output:
        return output["last_frame_url"]

    if "last_frame_url" in result:
        return result["last_frame_url"]

    return None


class SeedanceText2VideoAPI:
    """Handles API calls to Seedance Text-to-Video service"""

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

    def generate_video(self, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        # 从环境变量获取模型名称
        lite_model = os.getenv('SEEDANCE_LITE_T2V_MODEL', 'doubao-seedance-1-0-lite-t2v-250428')
        pro_model = os.getenv('SEEDANCE_PRO_MODEL', 'doubao-seedance-1-0-pro-250528')

        # 映射用户选择到实际模型名称
        model_mapping = {
            'seedance-1-0-lite-t2v-250428': lite_model,
            'seedance-1-0-pro-250528': pro_model,
            'doubao-seedance-1-0-lite-t2v-250428': lite_model,
            'doubao-seedance-1-0-pro-250528': pro_model,
        }
        actual_model = model_mapping.get(params.get('model'), lite_model)
        text_content = prompt
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
            "return_last_frame": True,  # 布尔值，用于获取最后一帧图片
            "content": [{"type": "text", "text": text_content}],
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
            timeout=60,
        )
        r.raise_for_status()
        return r.json()

    def wait_for_completion(
        self,
        task_id: str,
        max_wait_time: int = 300,
        poll_interval: int = 5,
    ) -> Dict[str, Any]:
        start = time.time()
        while time.time() - start < max_wait_time:
            result = self.get_task_status(task_id)
            status = result.get('status')

            if status == 'succeeded':
                return result
            if status == 'failed':
                raise RuntimeError(f"Video generation failed: {result.get('error', 'Unknown error')}")
            if status in ('queued', 'running'):
                time.sleep(poll_interval)
                continue

            raise RuntimeError(f"Unknown status: {status}")

        raise RuntimeError(f"Task {task_id} did not complete within {max_wait_time} seconds")


class SeedanceText2VideoNode:
    """Seedance Text to Video 节点"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "A beautiful landscape with mountains and lakes"}),
                "model": (["doubao-seedance-1-0-lite-t2v-250428", "doubao-seedance-1-0-pro-250528"], {"default": "doubao-seedance-1-0-lite-t2v-250428"}),
                "resolution": (["480p", "720p", "1080p"], {"default": "720p"}),
                "aspect_ratio": (["16:9", "4:3", "1:1", "3:4", "9:16", "21:9"], {"default": "16:9"}),
                "duration": ("INT", {"default": 5, "min": 3, "max": 12, "step": 1, "display": "slider"}),
                "seed": ("INT", {"default": 1, "min": -1, "max": 2**32 - 1, "step": 1}),
                "camera_fixed": ("BOOLEAN", {"default": False}),
                "watermark": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("VIDEO", "IMAGE", "STRING")
    RETURN_NAMES = ("video", "last_frame", "response_info")
    FUNCTION = "generate"
    CATEGORY = "BytePlus/Seedance Text to Video"   # ← 你想要的分组名称
    OUTPUT_NODE = True

    def _format_response_info(self, submit_resp: Dict[str, Any], done: Dict[str, Any], 
                             video_url: str, last_frame_url: str) -> str:
        """格式化API响应信息为可读的字符串"""
        info_lines = [
            "=== Seedance API 响应信息 ===",
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
            api = SeedanceText2VideoAPI()
            params = {
                "model": model,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "duration": duration,
                "camera_fixed": camera_fixed,
                "watermark": watermark,
            }
            if seed != -1:
                params["seed"] = seed

            print("[Seedance] Submitting video generation task...")
            submit_resp = api.generate_video(prompt, params)
            
            # 增强的API响应信息输出
            print("=" * 60)
            print("[Seedance] 📤 API提交响应详情:")
            print(f"  🆔 任务ID: {submit_resp.get('id', 'N/A')}")
            print(f"  📊 状态: {submit_resp.get('status', 'N/A')}")
            print(f"  🕐 创建时间: {submit_resp.get('created_at', 'N/A')}")
            print(f"  📝 完整响应: {submit_resp}")
            print("=" * 60)
            
            task_id = submit_resp.get("id") or submit_resp.get("task_id")
            if not task_id:
                raise RuntimeError(f"Failed to get task ID from API response: {submit_resp}")
            print(f"[Seedance] Task ID: {task_id}")

            print("[Seedance] Waiting for video generation to complete...")
            done = api.wait_for_completion(task_id)
            
            # 增强的完成响应信息输出
            print("=" * 60)
            print("[Seedance] ✅ 任务完成响应详情:")
            print(f"  🆔 任务ID: {done.get('id', 'N/A')}")
            print(f"  📊 最终状态: {done.get('status', 'N/A')}")
            print(f"  🕐 更新时间: {done.get('updated_at', 'N/A')}")
            print(f"  🎬 视频信息: {done.get('result', {})}")
            print(f"  📝 完整响应: {done}")
            print("=" * 60)

            video_url = _extract_video_url_from_result(done)
            if not video_url:
                raise RuntimeError(f"No video URL in completed result. Response: {done}")
            print(f"[Seedance] Video URL: {video_url}")

            # 提取last_frame_url
            last_frame_url = _extract_last_frame_url_from_result(done)
            print(f"[Seedance] Last Frame URL: {last_frame_url}")

            # 下载并封装为真正的 VIDEO 对象
            video_obj = download_url_to_video_output(video_url)
            
            # 下载并封装为 IMAGE 对象
            last_frame_obj = None
            if last_frame_url:
                try:
                    last_frame_obj = download_url_to_image_output(last_frame_url)
                    print("[Seedance] Last frame image downloaded successfully")
                except Exception as img_e:
                    print(f"[Seedance] Warning: Failed to download last frame image: {img_e}")
                    # 如果图片下载失败，创建一个空的占位图片
                    import torch
                    last_frame_obj = torch.zeros((1, 512, 512, 3), dtype=torch.float32)

            status = done.get("status", "unknown")
            
            # 生成响应信息摘要
            response_info = self._format_response_info(submit_resp, done, video_url, last_frame_url)
            
            # 最终结果摘要输出
            print("=" * 60)
            print("[Seedance] 🎉 生成任务完成摘要:")
            print(f"  ✅ 状态: {status}")
            print(f"  🆔 任务ID: {task_id}")
            print(f"  🎬 视频URL: {video_url}")
            print(f"  🖼️  最后一帧URL: {last_frame_url}")
            print(f"  📊 返回值: (VIDEO对象, IMAGE对象, 'response_info')")
            print("=" * 60)

            return (video_obj, last_frame_obj, response_info)

        except Exception as e:
            print(f"[Seedance] ❌ 生成视频时出错: {str(e)}")
            
            # 错误情况下的响应信息
            from datetime import datetime
            error_response_info = f"=== Seedance API 错误信息 ===\n错误: {str(e)}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # 返回错误时也要保持输出格式一致
            import torch
            empty_image = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
            empty_video = create_empty_video_object()
            return (empty_video, empty_image, error_response_info)


NODE_CLASS_MAPPINGS = {
    "SeedanceText2Video": SeedanceText2VideoNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SeedanceText2Video": "ByteDance Text to Video",
}
