# Seedance Text-to-Video ComfyUI Node

A ComfyUI custom node for generating videos using BytePlus Seedance Text-to-Video API.

## Features

- **Text-to-Video Generation**: Generate high-quality videos from text prompts
- **Multiple Models**: Support for both lite and pro models
- **Flexible Parameters**: Full control over resolution, aspect ratio, duration, and more
- **ComfyUI Integration**: Seamless integration with ComfyUI workflows
- **Video Processing**: Automatic video download and tensor conversion

## Installation

1. Clone or download this repository to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes/
   git clone <repository-url> Seedance-Text2Video
   ```

2. Install the required dependencies:
   ```bash
   cd Seedance-Text2Video
   pip install -r requirements.txt
   ```

3. Set up your API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your ARK_API_KEY
   ```

## Requirements

- Python 3.8+
- ComfyUI
- requests>=2.28.0
- python-dotenv>=0.19.0
- opencv-python>=4.5.0
- torch>=1.9.0
- numpy>=1.21.0
- Valid BytePlus ARK API Key

## Configuration

1. Get your API key from [BytePlus Console](https://console.byteplus.com/)
2. Copy `.env.example` to `.env`
3. Add your API key to the `.env` file:
   ```
   ARK_API_KEY=your_actual_api_key_here
   ```

## Usage

1. Restart ComfyUI after installation
2. Find the "ByteDance Text to Video" node in the "BytePlus/Seedance" category
3. Connect the node to your workflow
4. Configure the parameters:
   - **Prompt**: Your text description for the video
   - **Model**: Choose between lite and pro models
   - **Resolution**: 480p, 720p, or 1080p
   - **Aspect Ratio**: 16:9, 4:3, 1:1, 3:4, 9:16, 21:9
   - **Duration**: 3-12 seconds
   - **Seed**: Random seed for generation (-1 for random)
   - **Camera Fixed**: Whether to fix the camera position
   - **Watermark**: Whether to add watermarks to the output
   - **Control After Generate**: Seed control behavior

## Parameters

### Model
- `seedance-1-0-lite-t2v-250428`: Lite model for faster generation
- `seedance-1-0-pro-250528`: Pro model for higher quality

### Resolution
- `480p`: 480p resolution
- `720p`: 720p resolution (default for lite model)
- `1080p`: 1080p resolution (default for pro model)

### Aspect Ratio
- `16:9`: Widescreen (default)
- `4:3`: Standard
- `1:1`: Square
- `3:4`: Portrait
- `9:16`: Vertical
- `21:9`: Ultra-wide

### Duration
- Range: 3-12 seconds
- Default: 5 seconds

### Seed
- Range: -1 to 2^32-1
- -1: Random seed
- Other values: Fixed seed for reproducible results

### Camera Fixed
- `true`: Fix camera position
- `false`: Allow camera movement (default)

### Watermark
- `true`: Add watermarks (default)
- `false`: No watermarks

## Output

The node returns:
1. **Video**: ComfyUI standard IMAGE format tensor with shape [frames, height, width, channels]
2. **Status**: Generation status ("succeeded", "failed", etc.)
3. **Task ID**: Unique identifier for the generation task

The video tensor is in RGB format with pixel values normalized to 0-1 range, compatible with other ComfyUI video processing nodes.

## API Reference

This node uses the BytePlus Seedance API. For detailed API documentation, see:
- [Creating a video generation task](https://docs.byteplus.com/en/docs/ModelArk/1520757)

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your ARK_API_KEY is correctly set in the .env file
2. **Import Errors**: Install all required dependencies using `pip install -r requirements.txt`
3. **Video Processing Errors**: Ensure opencv-python, torch, and numpy are properly installed
4. **Generation Timeout**: Large videos may take longer to generate; the node waits up to 5 minutes by default

### Error Messages

- `ARK_API_KEY environment variable is required`: Set up your .env file with the API key
- `Video processing dependencies not available`: Install opencv-python, torch, and numpy
- `Task did not complete within X seconds`: Generation timeout, try again or use shorter duration

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Verify your API key and dependencies
3. Check ComfyUI console for detailed error messages