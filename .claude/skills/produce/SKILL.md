---
name: produce
description: 根据素材清单组装生成最终视频，调用AI生图、TTS配音、字幕合成等工具完成视频制作。使用场景：素材准备完毕后需要组装视频时触发。
argument-hint: "[选题ID|素材目录] [--account slug]"
---

# /produce - 视频制作

## 描述
根据素材清单，生成AI生图指引、TTS配音、字幕合成指引，最终组装为可发布的短视频。

## 账号感知

本 Skill 在指定账号的上下文中运行：
- 通过 `--account {slug}` 参数指定账号
- 或使用当前会话中 `/account 切换` 设定的活跃账号
- 如果 `data/matrix.json` 中只有一个 active 账号，自动使用该账号

**账号上下文决定**：
- 从 `accounts/{slug}/topics.json` 查找选题和素材路径
- 从 `accounts/{slug}/account.json` 读取 TTS 配置和发布设置
- 制作指引和输出存入 `accounts/{slug}/content/`

## 使用方式
- `/produce {素材目录}` — 根据指定素材清单制作视频
- `/produce {选题ID}` — 根据选题ID查找素材并制作
- `/produce 检查 {选题ID}` — 检查某个选题的素材完备性

## 执行流程

### 1. 读取素材清单
- 如果给了选题ID，在 `accounts/{slug}/topics.json` 中查找 `materialPath`
- 读取 `accounts/{slug}/{materialPath}/manifest.md`
- 检查所需素材的完备性
- 如果有缺失素材，提示用户先运行 `/material` 补充

### 2. AI生图指引
对每个场景：
- 读取 `prompts/scene-XX.txt` 中的提示词
- 推荐工具：即梦 > Midjourney > DALL-E / GPT-Image > Stable Diffusion
- 输出路径：`accounts/{slug}/content/materials/{标题}/images/scene-XX.png`

### 3. TTS配音
- 读取 `tts-text.txt`
- 从 `accounts/{slug}/account.json` 的 `tts` 字段获取推荐音色和语速
- 推荐 TTS 工具（按优先级）：
  1. **剪映TTS**（免费、中文最佳）
  2. **Edge TTS**（命令行自动化）
  3. **Azure TTS**（高品质）
- 如果使用自动化脚本：`python scripts/assemble.py --account {slug} {topic-id}`

### 4. 配乐获取
- 推荐搜索关键词和来源
- 配乐保存到 `accounts/{slug}/content/materials/{标题}/audio/bgm.mp3`

### 5. 视频组装指引
输出详细的剪映/CapCut组装指引，或提示使用自动化脚本：

```bash
# 自动化组装（推荐）
python scripts/assemble.py --account {slug} {topic-id}

# 前提：images/ 目录已放入场景图，可选 audio/bgm.mp3
```

手动组装指引包括：项目设置、轨道安排、转场效果、图片动效、字幕样式。

### 6. 输出成品
- 导出设置：1080x1920，30fps，H.264
- 文件保存到 `accounts/{slug}/content/output/YYYY-MM-DD-{标题}.mp4`
- 生成发布元数据 `accounts/{slug}/content/output/YYYY-MM-DD-{标题}-meta.md`：
  - 从 `account.json` 读取 `publishing.defaultTags` 和 `publishing.bestTimes`
  - 合并脚本中的话题标签

### 7. 更新选题状态
- 将选题状态更新为 `produced`
- 更新 `outputPath` 字段

## 自动化程度

| 步骤 | 自动化程度 | 说明 |
|------|-----------|------|
| 素材清单解析 | 全自动 | Claude直接处理 |
| AI生图提示词 | 全自动 | Claude生成 |
| AI生图执行 | 需手动 | 用户在即梦/MJ等工具中执行 |
| TTS配音 | 自动化 | `assemble.py` 调用 edge-tts |
| 配乐获取 | 需手动 | 用户在音乐库中搜索 |
| 视频组装 | 自动化 | `assemble.py` 调用 FFmpeg |
| 发布元数据 | 全自动 | Claude生成 |

## 注意事项
- 视频首帧（封面）决定点击率
- AI生成的图片需人工检查
- 配音语速建议每分钟200-250字
- BGM音量不要盖过配音（配音:BGM = 7:3）
- 导出前通读字幕，修正错别字
