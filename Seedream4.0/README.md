# Seedream 4.0 ComfyUI Node

这是一个用于 ComfyUI 的 Seedream 4.0 自定义节点，允许您通过 API 调用 BytePlus Seedream 4.0 图像生成服务。

## 功能特性

- **文生图 (Text to Image)**: 使用文本提示生成高质量图像
- **图生图 (Image to Image)**: 基于现有图像进行风格转换或修改
- 支持多种尺寸预设和自定义分辨率
- 支持批量生成（最多4张）
- 可控的种子值和生成参数
- 支持水印开关

## 安装说明

1. 将此文件夹复制到您的 ComfyUI `custom_nodes` 目录：
   ```bash
   cd ComfyUI/custom_nodes
   git clone [your-repo-url] Seedream4.0
   ```

2. 安装依赖：
   ```bash
   cd Seedream4.0
   pip install -r requirements.txt
   ```

3. 重启 ComfyUI

## 使用方法

### 配置 API Key

1. 访问 [BytePlus Seedream API 文档](https://docs.byteplus.com/en/docs/ModelArk/1541523) 申请 API Key
2. 在节点文件夹中创建 `.env` 文件：
   ```bash
   cp .env.example .env
   ```
3. 编辑 `.env` 文件，填入您的 API Key：
   ```
   ARK_API_KEY=your_actual_api_key_here
   MODEL_SEEDANCE_ID=seedream-4-0-250828
   ```

### 环境变量说明

- **ARK_API_KEY**: BytePlus ARK API 密钥
- **MODEL_SEEDANCE_ID**: Seedream 模型ID，默认为 `seedream-4-0-250828`，可根据需要调整

### 节点参数说明

#### Seedream 4.0 (文生图)

- **prompt**: 图像生成提示词
- **model**: 模型选择（从环境变量 MODEL_SEEDANCE_ID 读取默认值）
- **size_preset**: 尺寸预设（Custom, 2048x2048 (1:1), 2304x1728 (4:3), 1728x2304 (3:4), 2560x1440 (16:9), 1440x2560 (9:16), 2496x1664 (3:2), 1664x2496 (2:3), 3024x1296 (21:9), 4096x4096 (1:1)）
- **width/height**: 自定义宽高（512-4096像素，仅在 Custom 模式下使用）
- **sequential_image_generation**: 顺序生成模式（disabled/auto）
- **max_images**: 生成图像数量（1-15，但输入图像+生成图像总数不能超过15）
- **input_images**: 输入图像（可选，仅在 auto 模式下使用）
- **seed**: 随机种子（0为随机）
- **watermark**: 是否添加水印
- **image_encoding**: 图像编码方式（url/base64，默认 base64）

## 示例工作流

1. 配置 `.env` 文件中的 API Key
2. 添加 "Seedream 4.0" 节点
3. 输入提示词，如："a beautiful landscape with mountains and lake"
4. 调整参数（可选）
5. 连接到预览图像节点
6. 运行工作流

## 注意事项

- API 调用需要网络连接
- 生成时间取决于图像尺寸和数量，通常需要 10-60 秒
- 请妥善保管您的 API Key，不要将 `.env` 文件提交到版本控制
- API 调用可能产生费用，请查看 BytePlus 定价

## 故障排除

如果遇到问题：

1. 检查 `.env` 文件中的 `ARK_API_KEY` 是否正确配置
2. 确保网络连接正常
3. 查看 ComfyUI 控制台输出的错误信息
4. 确认依赖包已正确安装（特别是 `python-dotenv`）

## 支持

如有问题，请访问 [BytePlus 支持文档](https://docs.byteplus.com/) 或提交 Issue。