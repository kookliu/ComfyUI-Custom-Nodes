# ComfyUI BytePlus Custom Nodes

[中文文档](./README_CN.md) | English

A collection of ComfyUI custom nodes integrating BytePlus APIs for advanced image and video generation capabilities.

## 🎯 Features

### Video Generation Nodes

#### 1. **Seedance Text2Video**
- Generate videos from text descriptions
- Multiple resolutions (480p, 720p, 1080p)
- Various aspect ratios (16:9, 4:3, 1:1, 3:4, 9:16, 21:9)
- Adjustable duration (3-12 seconds)
- Model: `seedance-1-0-lite-t2v-250428`

#### 2. **Seedance Image2Video**
- Transform static images into dynamic videos
- Image animation support
- Adaptive aspect ratio option
- Model: `seedance-1-0-lite-i2v-250428`

#### 3. **Seedance Refs2Video**
- Generate videos from reference images
- Support for multiple reference image inputs
- Style transfer video generation

#### 4. **Seedance FirstLastFrame**
- Interpolate videos between first and last frames
- Control video start and end frames
- Smooth transition animation generation

### Image Generation Node

#### 5. **Seedream 4.0**
- High-quality text-to-image generation
- Image editing and enhancement support
- Resolution up to 2048x2048
- Sequential image generation mode
- Model: `doubao-seedream-4-0-250828`

## 📦 Installation

### 1. Clone the repository

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/yourusername/comfyui-byteplus-nodes.git
```

### 2. Install dependencies

```bash
cd comfyui-byteplus-nodes
pip install -r requirements.txt
```

### 3. Configure API Keys

Create `.env` files in each node directory with your BytePlus API key:

```bash
# Create .env file in each node directory
echo "ARK_API_KEY=your_api_key_here" > Seedream4.0/.env
echo "ARK_API_KEY=your_api_key_here" > Seedance-Text2Video/.env
echo "ARK_API_KEY=your_api_key_here" > Seedance-Image2Video/.env
echo "ARK_API_KEY=your_api_key_here" > Seedance-Refs2Video/.env
echo "ARK_API_KEY=your_api_key_here" > Seedance-FirstLastFrame/.env
```

Optional: Configure API endpoint (defaults to China Beijing region):
```bash
ARK_API_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

Supported API endpoints:
- China Beijing: `https://ark.cn-beijing.volces.com/api/v3`
- Southeast Asia: `https://ark.ap-southeast.bytepluses.com/api/v3`

### 4. Restart ComfyUI

## 🚀 Usage

### Using in ComfyUI

1. **Start ComfyUI**
2. **Add nodes**:
   - Right-click on the workspace
   - Select "Add Node" → "BytePlus"
   - Choose the desired node type

### Node Parameters

#### Seedance Text2Video
- **prompt**: Text description of video content
- **resolution**: Video resolution (480p/720p/1080p)
- **aspect_ratio**: Aspect ratio selection
- **duration**: Video duration in seconds (3-12)
- **seed**: Random seed (0 for random)

#### Seedance Image2Video
- **image**: Input image (ComfyUI IMAGE format)
- **prompt**: Animation effect description
- **resolution**: Output video resolution
- **duration**: Video duration

#### Seedream 4.0
- **prompt**: Image description text
- **width/height**: Output image dimensions
- **seed**: Random seed for reproducibility
- **sequential_image_generation**: Sequential generation mode
- **watermark**: Add watermark option

## 📊 Workflow Examples

### Text to Video
```
[Text Input] → [Seedance Text2Video] → [Video Output]
```

### Image Animation
```
[Load Image] → [Seedance Image2Video] → [Video Output]
```

### Combined Image Generation and Animation
```
[Text Input] → [Seedream 4.0] → [Seedance Image2Video] → [Video Output]
```

## 🔧 Troubleshooting

### Common Issues

1. **API Key Error**
   - Verify `ARK_API_KEY` in `.env` files
   - Check API key validity

2. **Connection Timeout**
   - Check network connectivity
   - Verify correct API endpoint for your region

3. **Video Output Error**
   - Ensure all dependencies are installed
   - Check ComfyUI version compatibility (0.3.59+)

## 📄 Requirements

- Python 3.8+
- ComfyUI 0.3.59 or higher
- Required packages:
  - requests
  - Pillow
  - numpy
  - torch
  - python-dotenv

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📜 License

MIT License

## 🔗 Links

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [BytePlus API Documentation](https://docs.byteplus.com/)
- [Get BytePlus API Key](https://console.byteplus.com/)

## 💡 Notes

- Video generation may take 30-300 seconds, please be patient
- API calls incur charges, check BytePlus pricing
- Use lower resolutions and shorter durations for testing to save costs

## 📮 Support

For issues or help, please open an [Issue](https://github.com/yourusername/comfyui-byteplus-nodes/issues)