# Seedance Image2Video ComfyUI Node

这是一个用于ComfyUI的自定义节点，实现了BytePlus Seedance的Image-to-Video功能。

## 功能特性

- 支持从图片生成视频
- 支持多种分辨率：480p, 720p, 1080p
- 支持多种宽高比：16:9, 4:3, 1:1, 3:4, 9:16, 21:9, adaptive
- 可调节视频时长：3-12秒
- 支持种子控制和相机固定选项
- 支持水印开关

## 安装

1. 将此目录复制到ComfyUI的`custom_nodes`文件夹中
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 配置API密钥：
   - 复制`.env.example`为`.env`
   - 在`.env`文件中设置你的`ARK_API_KEY`

## 使用方法

1. 在ComfyUI中找到"BytePlus/Seedance Image to Video"分类
2. 添加"ByteDance Image to Video"节点
3. 连接图片输入
4. 配置参数：
   - **image**: 输入图片
   - **prompt**: 文本提示词（可选）
   - **model**: 使用的模型
     - seedance-1-0-lite-i2v-250428（默认，轻量版）
     - seedance-1-0-pro-250528（专业版）
   - **resolution**: 视频分辨率
   - **aspect_ratio**: 宽高比
   - **duration**: 视频时长（3-12秒，支持0.5秒步进，滑块控制）
   - **seed**: 随机种子
   - **camera_fixed**: 是否固定相机
   - **watermark**: 是否添加水印

## API参数说明

基于BytePlus ModelArk API文档：https://docs.byteplus.com/en/docs/ModelArk/1520757

- **resolution**: 输出视频分辨率（480p/720p/1080p）
- **aspect_ratio**: 视频宽高比，adaptive表示自适应
- **duration**: 视频时长，范围3-12秒
- **seed**: 控制随机性的种子值，-1表示随机
- **camera_fixed**: 是否固定相机视角
- **watermark**: 是否在视频上添加水印

## 注意事项

- 需要有效的BytePlus ARK API密钥
- 图片会自动转换为base64格式上传
- 生成过程可能需要几分钟时间
- 确保网络连接稳定