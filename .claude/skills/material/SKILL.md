---
name: material
description: 根据视频脚本采集和生成素材，包括AI生图、配音文本提取、配乐推荐。使用场景：脚本完成后需要准备制作素材时触发。
argument-hint: "[选题ID|脚本路径|批量] [--account slug]"
---

# /material - 素材采集与生成

## 描述
根据视频脚本中的分镜描述，生成AI图片提示词、提取配音文本、整理配乐需求，输出可直接用于视频制作的素材清单。

## 账号感知

本 Skill 在指定账号的上下文中运行：
- 通过 `--account {slug}` 参数指定账号
- 或使用当前会话中 `/account 切换` 设定的活跃账号
- 如果 `data/matrix.json` 中只有一个 active 账号，自动使用该账号

**账号上下文决定**：
- 从 `accounts/{slug}/topics.json` 查找选题和脚本路径
- 从 `accounts/{slug}/account.json` 读取 TTS 配置（音色、语速）
- 素材输出到 `accounts/{slug}/content/materials/`

## 使用方式
- `/material {脚本路径}` — 为指定脚本生成素材清单
- `/material {选题ID}` — 根据选题ID查找对应脚本并生成素材
- `/material 批量` — 为所有 scripted 状态的选题生成素材

## 执行流程

### 1. 读取脚本
- 如果给了选题ID，在 `accounts/{slug}/topics.json` 中查找，获取 `scriptPath`
- 读取 `accounts/{slug}/{scriptPath}` 获取脚本内容
- 如果用 `批量`，扫描所有 status="scripted" 的选题

### 2. 解析分镜
从脚本中提取每个分镜的：
- **画面描述**（AI生图提示词）
- **配音文本**
- **字幕重点**
- **配乐建议**

### 3. 生成素材清单

保存到 `accounts/{slug}/content/materials/YYYY-MM-DD-{标题}/manifest.md`

### 4. 优化AI生图提示词
- 确保使用英文
- 添加风格关键词（digital art, cinematic lighting, 4K, detailed）
- 添加负面提示词（blurry, low quality, text, watermark）
- 统一视觉风格
- 添加竖屏构图提示（vertical composition, 9:16 aspect ratio）

### 5. 生成TTS配音文本
- 将所有分镜的配音文本按顺序拼接
- 标注停顿位置（`...`）
- 标注语气变化（`【加重】` `【放慢】` `【兴奋】`）
- **TTS 音色参考**：从 `accounts/{slug}/account.json` 的 `tts` 字段读取推荐音色
- 输出到 `accounts/{slug}/content/materials/YYYY-MM-DD-{标题}/tts-text.txt`

### 6. 生成字幕草稿
- 根据预估时长分配时间码
- 输出 SRT 格式到 `accounts/{slug}/content/materials/YYYY-MM-DD-{标题}/subtitles.srt`

### 7. 更新选题状态
- 将选题状态更新为 `material-ready`
- 更新 `materialPath` 字段

## 输出结构

```
accounts/{slug}/content/materials/YYYY-MM-DD-{标题}/
├── manifest.md          # 素材清单总览
├── prompts/             # AI生图提示词
│   ├── scene-00-hook.txt
│   ├── scene-01-xxx.txt
│   └── ...
├── tts-text.txt         # TTS配音完整文本
└── subtitles.srt        # 字幕草稿
```

## 注意事项
- AI生图提示词要尽可能详细
- 同一视频所有图片保持一致的视觉风格和色调
- TTS文本要口语化
- 字幕时间码是预估值，实际制作时需根据配音时长微调
