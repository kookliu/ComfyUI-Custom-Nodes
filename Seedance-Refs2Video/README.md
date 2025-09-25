# Seedance Reference Images to Video ComfyUI Node

这是一个ComfyUI自定义节点，用于调用Seedance的Reference Images to Video API，支持使用1-4张参考图片生成视频。

## 特性

- 支持1-4张参考图片输入（最少1张，最多4张）
- 完整的UI参数界面，包括分辨率、宽高比、时长滑块等
- 支持自定义API密钥配置
- 异步任务处理，自动等待视频生成完成
- 完善的错误处理和占位视频机制
- 返回标准的ComfyUI视频对象

## 安装

1. 将整个 `Seedance-Refs2Video` 文件夹复制到你的 ComfyUI 的 `custom_nodes` 目录下

2. 安装依赖包：
```bash
cd ComfyUI/custom_nodes/Seedance-Refs2Video
pip install -r requirements.txt
```

3. 配置API密钥：
   - 复制 `.env.example` 为 `.env`
   - 在 `.env` 文件中设置你的API密钥：
   ```
   ARK_API_KEY=your_api_key_here
   ```

4. 重启ComfyUI

## 使用方法

1. 在ComfyUI中找到 "ByteDance/Seedance" 分类
2. 添加 "Seedance Reference Images to Video" 节点
3. 连接1-4张图片到节点的image输入端口（image1, image2, image3, image4）
4. 设置生成参数：
   - **prompt**: 描述视频内容的文本提示
   - **model**: 选择模型（目前支持 seedance-1-0-lite-i2v-250428）
   - **resolution**: 视频分辨率（480p, 720p, 1080p）
   - **aspect_ratio**: 宽高比（16:9, 4:3, 1:1, 3:4, 9:16, 21:9）
   - **duration**: 视频时长（3-12秒，滑块控制）
   - **seed**: 随机种子（-1到2^32-1）
   - **camera_fixed**: 是否固定摄像机
   - **watermark**: 是否添加水印
5. 运行工作流生成视频

## API参数说明

- **model**: `seedance-1-0-lite-i2v-250428` - Seedance视频生成模型
- **resolution**: 视频分辨率选项
  - `480p`: 480p分辨率
  - `720p`: 720p分辨率  
  - `1080p`: 1080p分辨率
- **aspect_ratio**: 视频宽高比
  - `16:9`: 标准宽屏比例
  - `4:3`: 传统电视比例
  - `1:1`: 正方形
  - `3:4`: 竖屏比例
  - `9:16`: 手机竖屏比例
  - `21:9`: 超宽屏比例
- **duration**: 视频时长，3-12秒可调
- **seed**: 控制生成随机性的种子值
- **camera_fixed**: 是否固定摄像机视角
- **watermark**: 是否在视频上添加水印

## 输出说明

节点输出一个VIDEO对象，可以连接到：
- 视频预览节点
- 视频保存节点
- 其他支持视频输入的节点

## 注意事项

1. 确保至少连接1张参考图片，否则会报错
2. 最多支持4张参考图片
3. API调用需要网络连接和有效的API密钥
4. 视频生成可能需要几分钟时间，请耐心等待
5. 如果生成失败，节点会返回占位视频以避免工作流中断

## 技术实现

- 使用base64编码上传参考图片
- 支持异步任务处理和状态查询
- 完整的错误处理和重试机制
- 兼容ComfyUI的图像张量格式
- 环境变量配置管理