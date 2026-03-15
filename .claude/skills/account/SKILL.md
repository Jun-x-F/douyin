---
name: account
description: 管理矩阵账号：创建、切换、查看账号信息。使用场景：需要切换账号、创建新账号、查看账号状态时触发。
argument-hint: "[创建|切换|信息|赛道] [账号slug]"
---

# /account - 账号管理

## 描述
管理抖音矩阵账号，包括创建、切换、查看信息。所有内容操作（选题、脚本、素材、制作）都在当前活跃账号的上下文中执行。

## 使用方式
- `/account` — 列出所有账号及状态
- `/account 创建 {slug}` — 交互式创建新账号
- `/account 切换 {slug}` — 设置当前活跃账号
- `/account 信息 {slug}` — 查看账号详情和统计
- `/account 赛道` — 列出所有赛道和下属账号

## 核心概念

### 账号 Slug
每个账号有唯一的 slug 标识（如 `ai-tools-01`、`healing-01`），用于目录命名和 Skill 参数。

### 账号隔离
- 每个账号有独立的选题库、内容目录和发布历史
- 内容严格隔离，不跨账号共享脚本或素材
- 去重检查仅在同一账号内进行

## 执行流程

### 列出所有账号（`/account`）

1. 读取 `data/matrix.json`
2. 以表格形式展示：

| 账号 | 赛道 | 状态 | 已发布 | 待处理 |
|------|------|------|--------|--------|
| ai-tools-01 | 知识/教程 | active | 0 | 7 |

3. 对每个账号，读取 `accounts/{slug}/topics.json` 统计选题数量
4. 对每个账号，读取 `accounts/{slug}/published.json` 统计发布数量

### 创建新账号（`/account 创建 {slug}`）

1. 检查 slug 不与已有账号冲突
2. 向用户询问：
   - **赛道**：从 `data/matrix.json` 的 tracks 中选择
   - **账号名称**：如"AI效率达人"
   - **人设描述**：一句话定位
   - **目标受众**：年龄段和人群
   - **内容风格**：语气和特色
   - **TTS音色**：推荐可选项
3. 创建目录结构：
   ```
   accounts/{slug}/
   ├── account.json
   ├── topics.json      （空初始化）
   ├── published.json    （空初始化）
   └── content/
       ├── scripts/
       ├── materials/
       └── output/
   ```
4. 将账号注册到 `data/matrix.json` 的 accounts 数组
5. 如果有 `data/topics/pending-{track}.json`，提示用户是否将暂存选题导入

### 切换账号（`/account 切换 {slug}`）

1. 验证账号存在于 `data/matrix.json`
2. 读取 `accounts/{slug}/account.json` 获取完整配置
3. 在响应中明确告知当前账号上下文：
   - 账号名称和赛道
   - 待处理选题数量
   - 最近的内容状态
4. 后续所有 Skill（/topic, /script, /material, /produce）将自动在此账号目录下操作

> **重要**：切换账号不会持久化到文件系统。在每个新的会话中，需要重新 `/account 切换`，或者在调用其他 Skill 时通过 `--account {slug}` 参数指定。

### 查看账号信息（`/account 信息 {slug}`）

1. 读取 `accounts/{slug}/account.json`
2. 读取 `accounts/{slug}/topics.json`
3. 读取 `accounts/{slug}/published.json`
4. 展示：
   - 账号配置（人设、风格、TTS设置等）
   - 选题统计（按状态分组）
   - 发布历史摘要
   - 最近一次发布的表现数据（如有）

### 查看赛道（`/account 赛道`）

1. 读取 `data/matrix.json`
2. 按赛道分组展示账号：
   ```
   知识/教程
   ├── ai-tools-01 (active) — 7个选题, 0已发布

   情感/心理
   └── (暂无账号，有3个待分配选题)

   AI音乐
   └── (暂无账号)
   ```

## 数据文件路径

| 文件 | 作用 |
|------|------|
| `data/matrix.json` | 矩阵注册表（赛道定义 + 账号列表） |
| `accounts/{slug}/account.json` | 账号配置（人设/风格/TTS/发布设置） |
| `accounts/{slug}/topics.json` | 账号选题库 |
| `accounts/{slug}/published.json` | 发布历史 |
| `data/topics/pending-{track}.json` | 待分配选题（创建新赛道账号时导入） |

## 注意事项
- 账号 slug 一旦创建不可修改（因为关联了目录结构）
- 删除账号是高危操作，需二次确认，且不会物理删除目录
- 每个赛道建议最多 3 个账号，避免管理负担过重
- 新账号创建后，建议立即运行 `/topic` 生成首批选题
