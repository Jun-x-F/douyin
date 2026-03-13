# /topic - 选题策划

## 描述
基于调研数据和热点趋势，智能推荐视频选题，维护选题库。

## 使用方式
- `/topic` — 生成 5-10 个新选题推荐
- `/topic 热点` — 基于当日热点生成选题
- `/topic 状态 {id} {新状态}` — 更新选题状态（backlog/in-progress/published）
- `/topic 列表` — 查看当前选题库
- `/topic 清理` — 清理已过时的选题

## 执行流程

### 1. 收集背景信息
- 读取 `CLAUDE.md` 获取账号定位、赛道方向、视频形式
- 读取 `data/research/` 最新调研报告获取赛道洞察
- 读取 `data/topics/backlog.json` 查看已有选题避免重复
- 如有 `data/analytics/` 数据，参考历史表现数据

### 2. 热点调研
使用 WebSearch 搜索：
- "抖音今日热搜"
- "今日热点新闻事件"
- "抖音 {赛道} 最新热门"
- 与账号赛道相关的时事、节日、纪念日

### 3. 选题生成
为每个选题提供：
- **标题**：视频选题标题
- **类型**：ai-graphic / mashup / recreation / oral（根据内容匹配最适合的形式）
- **潜力评估**：high / medium / low
- **推荐理由**：为什么这个选题会火
- **建议标签**：相关话题标签
- **时效性**：常青内容 / 热点时效（标注截止日期）

选题原则：
- 优先推荐"高流量潜力 + 可自动化制作"的选题
- 热点类选题注明时效性
- 每批选题中混合常青内容和热点内容
- 避免与已有选题重复

### 4. 更新选题库
将新选题写入 `data/topics/backlog.json`，格式如下：

```json
{
  "id": "topic-{序号}",
  "title": "选题标题",
  "type": "ai-graphic | mashup | recreation | oral",
  "status": "backlog",
  "potential": "high | medium | low",
  "reason": "推荐理由",
  "tags": ["标签1", "标签2"],
  "timeliness": "evergreen | hot-until-YYYY-MM-DD",
  "createdAt": "YYYY-MM-DD"
}
```

更新 `lastUpdated` 字段为当前日期。

### 5. 输出展示
以表格形式展示推荐选题：

| # | 标题 | 类型 | 潜力 | 理由 |
|---|------|------|------|------|

并提示用户：
- 选定选题后可使用 `/script {选题标题}` 生成脚本
- 使用 `/topic 状态 {id} in-progress` 标记开始制作

## 状态管理命令

当用户使用 `/topic 状态` 时：
- 读取 `data/topics/backlog.json`
- 更新指定 id 的 status 字段
- 保存文件

当用户使用 `/topic 列表` 时：
- 读取 `data/topics/backlog.json`
- 按状态分组展示所有选题

## 注意事项
- 选题要具体，不要太宽泛（"如何提高效率" ✗ → "3个让你下班早2小时的Excel技巧" ✓）
- 标题本身就要有吸引力，像一个好的视频标题
- 每次生成的选题要多样化，覆盖不同视频形式
