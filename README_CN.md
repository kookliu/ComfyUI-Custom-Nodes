# ComfyUI BytePlus 自定义节点

中文文档 | [English](./README.md)

集成 BytePlus API 的 ComfyUI 自定义节点集合，提供先进的图像和视频生成功能。

## 🎯 功能特性

### 视频生成节点

#### 1. **Seedance 文本生成视频（Text2Video）**
- 从文本描述生成视频
- 支持多种分辨率（480p、720p、1080p）
- 多种宽高比（16:9、4:3、1:1、3:4、9:16、21:9）
- 可调时长（3-12秒）
- 模型：`seedance-1-0-lite-t2v-250428`

#### 2. **Seedance 图像生成视频（Image2Video）**
- 将静态图像转换为动态视频
- 图像动画化支持
- 自适应宽高比选项
- 模型：`seedance-1-0-lite-i2v-250428`

#### 3. **Seedance 参考图生成视频（Refs2Video）**
- 从参考图像生成视频
- 支持多个参考图像输入
- 风格迁移视频生成

#### 4. **Seedance 首尾帧生成视频（FirstLastFrame）**
- 首尾帧之间插值生成视频
- 控制视频起始和结束帧
- 平滑过渡动画生成

### 图像生成节点

#### 5. **Seedream 4.0**
- 高质量文本生成图像
- 图像编辑和增强支持
- 分辨率最高可达 2048x2048
- 序列图像生成模式
- 模型：`doubao-seedream-4-0-250828`

## 📦 安装步骤

### 1. 克隆仓库

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/kookliu/ComfyUI-Custom-Nodes.git
```

### 2. 安装依赖

```bash
cd ComfyUI-Custom-Nodes
pip install -r requirements.txt
```

### 3. 配置 API 密钥

在每个节点目录中创建 `.env` 文件并添加您的 BytePlus API 密钥：

```bash
# 在每个节点目录创建 .env 文件
echo "ARK_API_KEY=your_api_key_here" > Seedream4.0/.env
echo "ARK_API_KEY=your_api_key_here" > Seedance-Text2Video/.env
echo "ARK_API_KEY=your_api_key_here" > Seedance-Image2Video/.env
echo "ARK_API_KEY=your_api_key_here" > Seedance-Refs2Video/.env
echo "ARK_API_KEY=your_api_key_here" > Seedance-FirstLastFrame/.env
```

可选：配置 API 端点（默认为中国北京区域）：
```bash
ARK_API_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

支持的 API 端点：
- 中国北京：`https://ark.cn-beijing.volces.com/api/v3`
- 东南亚：`https://ark.ap-southeast.bytepluses.com/api/v3`

### 4. 重启 ComfyUI

## 🚀 使用方法

### 在 ComfyUI 中使用

1. **启动 ComfyUI**
2. **添加节点**：
   - 在工作区右键点击
   - 选择 "Add Node" → "BytePlus"
   - 选择所需的节点类型

### 节点参数说明

#### Seedance 文本生成视频
- **prompt**：视频内容的文本描述
- **resolution**：视频分辨率（480p/720p/1080p）
- **aspect_ratio**：宽高比选择
- **duration**：视频时长（秒）（3-12）
- **seed**：随机种子（0 为随机）

#### Seedance 图像生成视频
- **image**：输入图像（ComfyUI IMAGE 格式）
- **prompt**：动画效果描述
- **resolution**：输出视频分辨率
- **duration**：视频时长

#### Seedream 4.0
- **prompt**：图像描述文本
- **width/height**：输出图像尺寸
- **seed**：随机种子（用于结果复现）
- **sequential_image_generation**：序列生成模式
- **watermark**：添加水印选项

## 📊 工作流示例

### 文本生成视频
```
[文本输入] → [Seedance Text2Video] → [视频输出]
```

### 图像动画化
```
[加载图像] → [Seedance Image2Video] → [视频输出]
```

### 图像生成与动画化组合
```
[文本输入] → [Seedream 4.0] → [Seedance Image2Video] → [视频输出]
```

## 🔧 故障排除

### 常见问题

1. **API 密钥错误**
   - 验证 `.env` 文件中的 `ARK_API_KEY`
   - 检查 API 密钥有效性

2. **连接超时**
   - 检查网络连接
   - 验证您所在区域的正确 API 端点

3. **视频输出错误**
   - 确保所有依赖项已安装
   - 检查 ComfyUI 版本兼容性（0.3.59+）

## 📄 系统要求

- Python 3.8+
- ComfyUI 0.3.59 或更高版本
- 必需的软件包：
  - requests
  - Pillow
  - numpy
  - torch
  - python-dotenv

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📜 许可证

MIT License

## 🔗 相关链接

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [BytePlus API 文档](https://docs.byteplus.com/)
- [获取 BytePlus API 密钥](https://console.byteplus.com/)

## 💡 注意事项

- 视频生成可能需要 30-300 秒，请耐心等待
- API 调用会产生费用，请查看 BytePlus 定价
- 建议在测试时使用较低分辨率和较短时长以节省成本

## 📮 技术支持

如有问题或需要帮助，请提交 [Issue](https://github.com/kookliu/ComfyUI-Custom-Nodes/issues)