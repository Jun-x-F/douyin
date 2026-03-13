# 抖音短视频副业项目

## 项目概述

这是一个从调研到全自动发布的抖音短视频副业项目，目标是通过系统化的内容生产流程实现高收益。

项目通过 Claude Code Skills 驱动各环节，形成完整的内容生产流水线。

## 账号定位

> 待通过 `/research` 赛道调研确定后填写

- **赛道方向**：待定
- **目标受众**：待定
- **账号人设**：待定
- **内容风格**：待定
- **差异化定位**：待定

## 视频形式

本项目支持四种视频制作形式：

| 形式 | 说明 | 适用场景 |
|------|------|---------|
| AI图文 | AI生成图片 + 配音 + 字幕，全自动化程度最高 | 知识科普、情感语录、历史故事 |
| 混剪 | 素材混合剪辑 + 解说配音 | 影视解说、热点盘点、好物合集 |
| 二创 | 基于已有素材二次创作 | 影视二创、游戏二创、热梗再造 |
| 口播 | 真人/虚拟人出镜讲解 | 知识分享、产品测评、观点输出 |

## 工作流程

标准内容生产流程（每个环节对应一个 Skill）：

```
/research 调研分析 → /topic 选题策划 → /script 脚本编写
    → /material 素材采集 → /produce 视频制作
    → /cover 封面标题 → /publish 发布管理
    → /analytics 数据分析 → /optimize 优化迭代
```

## Skill 使用指南

### P0 核心能力（已实现）

| 命令 | 功能 | 示例用法 |
|------|------|---------|
| `/research` | 赛道调研、竞品分析、关键词挖掘 | `/research` 或 `/research 知识赛道` |
| `/topic` | 热点选题、选题库管理 | `/topic` 生成选题 或 `/topic 更新状态` |
| `/script` | 多形式脚本生成 | `/script AI图文 选题标题` |

### P1 生产能力（待实现）

`/material` `/produce` `/cover` `/publish` `/analytics`

### P2 增长能力（待实现）

`/optimize` `/monetize` `/pipeline`

## 数据规范

### 文件命名
- 调研报告：`data/research/YYYY-MM-DD-{主题}.md`
- 视频脚本：`content/scripts/YYYY-MM-DD-{标题}.md`

### 选题库格式 (`data/topics/backlog.json`)

```json
{
  "topics": [
    {
      "id": "topic-001",
      "title": "选题标题",
      "type": "ai-graphic | mashup | recreation | oral",
      "status": "backlog | in-progress | published",
      "potential": "high | medium | low",
      "reason": "推荐理由",
      "createdAt": "2026-03-13",
      "tags": ["标签1", "标签2"]
    }
  ],
  "lastUpdated": "2026-03-13"
}
```

### 内容原则
- 开头 3 秒必须有强钩子（悬念/冲突/反差/共情）
- 节奏紧凑，避免冗余
- 结尾必须有互动引导（关注/点赞/评论）
- 遵守平台规则，不涉及敏感内容
