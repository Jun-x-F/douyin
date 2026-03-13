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

---

## 增强能力备忘（未来配置参考）

以下三项能力当前未启用，在项目发展到需要时参照配置。

### A. Agent 子代理（`.claude/agents/`）

**作用**：独立 AI 助手，有隔离上下文和定制工具。适合深度自治任务（深度调研、视频制作流水线），不占用主会话上下文。

**配置方式**：在项目根目录创建 `.claude/agents/{name}.md`：
```yaml
---
name: researcher
description: 深度调研子代理，用于赛道分析和竞品拆解
tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
model: sonnet
---
你是一个专业的短视频赛道分析师...（系统 prompt）
```

**可用字段**：

| 字段 | 说明 |
|------|------|
| `name` | 代理名称 |
| `description` | 描述和触发场景 |
| `tools` | 允许使用的工具列表 |
| `disallowedTools` | 禁止使用的工具 |
| `model` | 模型：`sonnet`/`opus`/`haiku` |
| `permissionMode` | 权限模式：`default`/`acceptEdits`/`dontAsk`/`plan` |
| `maxTurns` | 最大执行轮次 |
| `skills` | 预加载的 Skill |
| `mcpServers` | 可用的 MCP 服务器 |
| `memory` | 持久记忆：`user`/`project`/`local` |
| `background` | `true` 后台运行 |
| `isolation` | `worktree` 在隔离 git worktree 中运行 |

**计划创建的 Agent**：
- `researcher` — 深度调研（`model: sonnet`）
- `scriptwriter` — 脚本生成（`model: opus`，最高创意质量）
- `content-strategist` — 内容策略（`model: opus`, `memory: project`，跨会话积累知识）

### B. References 参考资料

**作用**：Skill 目录下的辅助文件，按需加载。解决 SKILL.md 过长问题，提供示例和参考库。

**配置方式**：在 Skill 目录下放文件，在 SKILL.md 中引用：
```
script/
├── SKILL.md
├── references/
│   ├── hook_patterns.md        # 爆款钩子模式库
│   └── example_scripts/        # 优秀脚本示例
└── scripts/
    └── helper.py               # 辅助脚本
```
在 SKILL.md 中写：`详见 [hook_patterns.md](references/hook_patterns.md)`

**计划创建的 References**：
- `script/references/hook_patterns.md` — 50+ 爆款钩子模式
- `script/references/example_scripts/` — 各类型优秀脚本示例
- `cover/references/title_formulas.md` — 30+ 标题公式
- `research/references/niche_taxonomy.md` — 赛道分类与评估框架

### C. Skill Frontmatter 高级配置

**所有可用字段**：

| 字段 | 说明 |
|------|------|
| `name` | Skill 名称，决定 `/slash-command`（默认用文件夹名） |
| `description` | 功能描述和触发场景 |
| `argument-hint` | 参数提示，如 `[赛道名]` |
| `disable-model-invocation` | `true` 阻止 Claude 自动触发（用于发布等有副作用的操作） |
| `user-invocable` | `false` 隐藏斜杠菜单（仅作背景知识） |
| `allowed-tools` | 限制可用工具，如 `Read, Grep, Glob` |
| `model` | 指定模型 |
| `context` | `fork` 在隔离子代理中运行 |
| `agent` | `context: fork` 时的子代理类型 |

**未来关键配置**：
- `/publish`：需设 `disable-model-invocation: true`（防止自动发布）
- `/pipeline`：可用 `context: fork` 委托子任务给 Agent
- `/analytics`：可用 `allowed-tools: Read, Grep, Glob` 限制只读
