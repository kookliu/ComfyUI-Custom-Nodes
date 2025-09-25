# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a ComfyUI custom node that integrates BytePlus Seedance Text-to-Video API. It allows users to generate videos from text prompts within ComfyUI workflows.

## Key Architecture

### API Integration
- **SeedanceText2VideoAPI**: Handles all BytePlus API communication
  - Requires `ARK_API_KEY` environment variable
  - Base URL: `https://ark.ap-southeast.bytepluses.com/api/v3`
  - Implements task submission and polling pattern

### ComfyUI Integration
- **SeedanceText2VideoNode**: ComfyUI node implementation
  - Returns `VIDEO` type (ComfyUI's VideoInput format)
  - Converts API video URLs to tensor format compatible with ComfyUI
  - Uses `VideoComponents` and `VideoFromComponents` for proper video handling

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add ARK_API_KEY

# Run linting (if basedpyright is available)
basedpyright nodes_seedance_text2video.py

# Test in ComfyUI
# Place this folder in ComfyUI/custom_nodes/ and restart ComfyUI
```

## Important Implementation Details

### Video Output Format
The node outputs VIDEO type using ComfyUI's video format:
- Downloads video from API URL to local MP4 file
- Converts to tensor format: `[frames, height, width, channels]`
- Wraps in `VideoComponents` with proper frame rate
- Returns `VideoFromComponents` object compatible with other ComfyUI video nodes

### API Response Structure
BytePlus API returns:
- Task submission: `{"id": "cgt-xxxx"}`
- Status check: `{"status": "succeeded", "content": {"video_url": "https://..."}}`

### Error Handling
- API key validation on initialization
- Timeout handling for long-running generation tasks (default 300s)
- Graceful fallback when video processing dependencies are missing
- Returns dummy video object on error to prevent workflow breakage