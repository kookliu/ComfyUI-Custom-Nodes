# Seedance First-Last Frame to Video ComfyUI Node

这是一个用于ComfyUI的自定义节点，实现了BytePlus Seedance的First-Last Frame to Video功能。通过提供首帧和尾帧图片，生成连接两帧的视频内容。

## 功能特性

- **双图片输入**：支持first_frame和last_frame两个图片输入
- **完整参数支持**：包含所有API参数（model、resolution、aspect_ratio、duration、seed、camera_fixed、watermark）
- **Base64图片上传**：自动将ComfyUI图片张量转换为base64格式上传
- **实时状态监控**：自动轮询任务状态直到完成
- **错误处理**：提供详细的错误信息和占位视频
- **视频对象返回**：返回标准的ComfyUI VIDEO对象

## 安装步骤

### 1. 复制文件
将整个`Seedance-FirstLastFrame`目录复制到ComfyUI的custom_nodes目录：
```bash
cp -r Seedance-FirstLastFrame /path/to/ComfyUI/custom_nodes/
```

### 2. 安装依赖
```bash
cd /path/to/ComfyUI/custom_nodes/Seedance-FirstLastFrame
pip install -r requirements.txt
```

### 3. 配置API密钥
在`Seedance-FirstLastFrame`目录下创建`.env`文件：
```bash
ARK_API_KEY=your_api_key_here
```

### 4. 重启ComfyUI
重启ComfyUI以加载新的自定义节点。

## 使用方法

1. 在ComfyUI中找到"BytePlus/Seedance First Last Frame to Video"分类
2. 添加"ByteDance First-Last Frame to Video"节点
3. 连接两个图片输入：
   - `first_frame`：首帧图片
   - `last_frame`：尾帧图片
4. 配置参数：
   - `prompt`：文本描述（默认："A blue-green jingwei bird transforms into a human form."）
   - `model`：模型选择（seedance-1-0-lite-i2v-250428）
   - `resolution`：分辨率（480p/720p/1080p）
   - `aspect_ratio`：宽高比（16:9/4:3/1:1/3:4/9:16/21:9/adaptive）
   - `duration`：视频时长（3-12秒，滑块控制）
   - `seed`：随机种子（-1到2^32-1）
   - `camera_fixed`：是否固定相机
   - `watermark`：是否添加水印
5. 运行工作流，节点将返回生成的视频

## API参数说明

### model
- 支持的模型：`seedance-1-0-lite-i2v-250428`

### resolution
- `480p`：480p分辨率
- `720p`：720p分辨率（默认）
- `1080p`：1080p分辨率

### aspect_ratio
- `16:9`：宽屏比例
- `4:3`：标准比例
- `1:1`：正方形
- `3:4`：竖屏比例
- `9:16`：手机竖屏
- `21:9`：超宽屏
- `adaptive`：自适应（默认）

### duration
- 范围：3-12秒
- 步长：0.5秒
- 默认：5秒
- UI：滑块控制

### seed
- 范围：-1到2^32-1
- -1表示随机种子
- 默认：1

### camera_fixed
- `true`：固定相机位置
- `false`：不固定相机（默认）

### watermark
- `true`：添加水印（默认）
- `false`：不添加水印

## 输出说明

节点返回三个输出：
1. `video`：生成的视频对象（VIDEO类型）
2. `status`：生成状态（"succeeded"或"failed: 错误信息"）
3. `task_id`：API任务ID（用于调试）

## 注意事项

1. **API密钥**：确保在`.env`文件中正确配置`ARK_API_KEY`
2. **网络连接**：需要稳定的网络连接访问BytePlus API
3. **图片格式**：支持ComfyUI标准的图片张量格式
4. **处理时间**：视频生成可能需要几分钟时间，请耐心等待
5. **错误处理**：如果生成失败，会返回错误占位视频和详细错误信息

## 技术实现

- 基于BytePlus Seedance API
- 支持ComfyUI 0.3.59和0.4.x版本
- 使用requests库进行HTTP请求
- 自动处理图片格式转换和base64编码
- 实现异步任务状态轮询机制