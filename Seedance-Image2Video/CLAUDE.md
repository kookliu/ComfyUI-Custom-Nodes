# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a ComfyUI custom node that implements BytePlus Seedance's Image-to-Video generation functionality. It allows users to generate videos from static images using the Seedance API.

## Setup Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API credentials (required before first use)
cp .env.example .env
# Then edit .env to add your ARK_API_KEY
```

## Key Architecture

### Main Components

1. **nodes_seedance_image2video.py**: Core node implementation
   - `SeedanceImage2VideoAPI`: Handles all API communications with BytePlus Seedance service
   - `SeedanceImage2VideoNode`: ComfyUI node class that integrates with the ComfyUI workflow system
   - Uses base URL: `https://ark.ap-southeast.bytepluses.com/api/v3`

2. **byteplus_video_utils.py**: Video handling utilities
   - `download_url_to_video_output()`: Downloads generated video and converts to ComfyUI video object
   - Implements multiple fallback methods for ComfyUI video object creation (compatible with versions 0.3.59+)

3. **__init__.py**: Module registration with ComfyUI
   - Exports NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS for ComfyUI integration

### API Integration Flow

1. Image is converted to base64 format using `_image_to_base64()`
2. API request is sent to `/contents/generations/tasks` with image and parameters
3. Task ID is returned and polled at `/contents/generations/tasks/{task_id}` until completion
4. Video URL is extracted from response and downloaded
5. Downloaded video is converted to ComfyUI VIDEO object for downstream processing

### Configuration

- API key must be set in environment variable `ARK_API_KEY` (loaded from `.env` file)
- Supports models: `seedance-1-0-lite-i2v-250428`
- Resolutions: 480p, 720p, 1080p
- Aspect ratios: 16:9, 4:3, 1:1, 3:4, 9:16, 21:9, adaptive
- Duration range: 3-12 seconds

### ComfyUI Integration

The node appears in ComfyUI under category "BytePlus/Seedance Image to Video" and accepts:
- IMAGE input (ComfyUI tensor format)
- Text prompt
- Various generation parameters (resolution, duration, seed, etc.)

Returns:
- VIDEO object for further processing in ComfyUI workflow
- Status string
- Task ID for reference