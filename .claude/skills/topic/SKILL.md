---
name: topic
description: 基于调研数据和热点趋势，智能推荐视频选题，维护选题库。使用场景：决定下一个视频内容、查看选题队列、用户问"发什么"时触发。
argument-hint: "[热点|列表|状态|去重检查] [--account slug]"
---

# /topic - 选题策划

## 描述
基于调研数据和热点趋势，智能推荐视频选题，维护选题库。

## 账号感知

本 Skill 在指定账号的上下文中运行：
- 通过 `--account {slug}` 参数指定账号
- 或使用当前会话中 `/account 切换` 设定的活跃账号
- 如果 `data/matrix.json` 中只有一个 active 账号，自动使用该账号
- 否则提示用户先选择账号

**账号上下文决定**：
- 选题写入哪个 `accounts/{slug}/topics.json`
- 从哪个 `accounts/{slug}/account.json` 读取赛道和风格配置
- 去重检查范围（同账号内的 `published.json`）

## 使用方式
- `/topic` — 为当前账号生成 5-10 个新选题推荐
- `/topic 热点` — 基于当日热点生成选题
- `/topic 状态 {id} {新状态}` — 更新选题状态
- `/topic 列表` — 查看当前账号选题库
- `/topic 清理` — 清理已过时的选题
- `/topic 去重检查` — 扫描当前账号选题与已发布内容的相似度

## 执行流程

### 1. 解析账号上下文
- 读取 `data/matrix.json` 获取账号列表
- 确定目标账号 slug
- 读取 `accounts/{slug}/account.json` 获取赛道、风格、受众信息

### 2. 收集背景信息
- 读取 `CLAUDE.md` 获取项目总览
- 读取 `data/research/` 最新调研报告获取赛道洞察
- 读取 `accounts/{slug}/topics.json` 查看已有选题避免重复
- 读取 `accounts/{slug}/published.json` 查看已发布内容避免重复

### 3. 热点调研
使用 WebSearch 搜索：
- "抖音今日热搜"
- "今日热点新闻事件"
- "抖音 {赛道关键词} 最新热门"
- 与账号赛道相关的时事、节日、纪念日

### 4. 去重检查
对每个候选选题：
- 与 `accounts/{slug}/topics.json` 中现有选题标题比对（关键词重叠度 > 60% 则跳过）
- 与 `accounts/{slug}/published.json` 中已发布标题比对
- 标记为"高价值可重发"的除外（`highValueRepost: true`）

### 5. 选题生成
为每个选题提供：
- **标题**：视频选题标题
- **类型**：ai-graphic / mashup / recreation / oral
- **潜力评估**：high / medium / low
- **推荐理由**：为什么这个选题会火
- **建议标签**：相关话题标签
- **时效性**：常青内容 / 热点时效

选题原则：
- 优先推荐"高流量潜力 + 可自动化制作"的选题
- 选题风格匹配 `account.json` 中定义的账号人设
- 热点类选题注明时效性
- 每批选题中混合常青内容和热点内容

### 6. 更新选题库
将新选题写入 `accounts/{slug}/topics.json`，格式如下：

```json
{
  "id": "topic-{nextId}",
  "title": "选题标题",
  "type": "ai-graphic | mashup | recreation | oral",
  "status": "backlog",
  "potential": "high | medium | low",
  "reason": "推荐理由",
  "tags": ["标签1", "标签2"],
  "timeliness": "evergreen | hot-until-YYYY-MM-DD",
  "createdAt": "YYYY-MM-DD",
  "scriptPath": null,
  "materialPath": null,
  "outputPath": null,
  "publishId": null
}
```

递增 `nextId`，更新 `lastUpdated`。

### 7. 输出展示
以表格形式展示推荐选题：

| # | 标题 | 类型 | 潜力 | 理由 |
|---|------|------|------|------|

并提示用户：
- 选定选题后可使用 `/script {选题标题}` 生成脚本
- 使用 `/topic 状态 {id} scripted` 标记进入下一阶段

## 状态管理

### 状态流转（5级）
```
backlog → scripted → material-ready → produced → published
```

当用户使用 `/topic 状态 {id} {新状态}` 时：
- 读取 `accounts/{slug}/topics.json`
- 更新指定 id 的 status 字段
- 保存文件

当用户使用 `/topic 列表` 时：
- 读取 `accounts/{slug}/topics.json`
- 按状态分组展示所有选题

## 注意事项
- 选题要具体，不要太宽泛
- 标题本身就要有吸引力，像一个好的视频标题
- 每次生成的选题要多样化，覆盖不同视频形式
- 选题内容必须匹配账号赛道定位，不要跨赛道推荐
