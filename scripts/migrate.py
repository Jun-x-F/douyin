#!/usr/bin/env python3
"""
矩阵化架构迁移脚本

将单账号项目结构迁移到多账号矩阵架构。
一次性执行，迁移完成后可删除。

用法: python scripts/migrate.py
"""

import json
import shutil
import os
from pathlib import Path
from datetime import date

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TODAY = date.today().isoformat()


def create_matrix_json():
    """创建矩阵注册表"""
    matrix = {
        "tracks": {
            "knowledge": {
                "name": "知识/教程",
                "description": "AI工具教学 / 效率提升 / 副业技能"
            },
            "emotion": {
                "name": "情感/心理",
                "description": "自我成长 / 职场心理 / 深夜治愈"
            },
            "ai-music": {
                "name": "AI音乐",
                "description": "AI音乐创作与翻唱"
            }
        },
        "accounts": [
            {
                "slug": "ai-tools-01",
                "name": "AI效率达人",
                "track": "knowledge",
                "status": "active",
                "createdAt": "2026-03-13"
            }
        ],
        "lastUpdated": TODAY
    }
    path = PROJECT_ROOT / "data" / "matrix.json"
    path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ {path.relative_to(PROJECT_ROOT)}")


def create_dedup_db():
    """创建去重指纹库"""
    dedup_dir = PROJECT_ROOT / "data" / "dedup"
    dedup_dir.mkdir(parents=True, exist_ok=True)
    fingerprints = {"fingerprints": [], "lastUpdated": TODAY}
    path = dedup_dir / "fingerprints.json"
    path.write_text(json.dumps(fingerprints, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ {path.relative_to(PROJECT_ROOT)}")


def create_account_structure(slug):
    """创建账号目录结构"""
    account_dir = PROJECT_ROOT / "accounts" / slug
    for sub in ["content/scripts", "content/materials", "content/output"]:
        (account_dir / sub).mkdir(parents=True, exist_ok=True)
    print(f"  ✓ accounts/{slug}/ 目录结构")


def create_account_json(slug):
    """创建账号配置"""
    account = {
        "slug": slug,
        "name": "AI效率达人",
        "track": "knowledge",
        "persona": "专注分享最新、最实用的AI工具和副业方法",
        "audience": "18-35岁，对AI工具感兴趣的职场人、学生、副业探索者",
        "style": {
            "tone": "实用干货，信息密度高，节奏紧凑",
            "hook": "先抛问题再给方案",
            "format": "ai-graphic"
        },
        "tts": {
            "voice": "zh-CN-YunxiNeural",
            "rate": "+10%"
        },
        "publishing": {
            "bestTimes": ["12:00-13:00", "20:00-22:00"],
            "avoidTimes": ["周末上午"],
            "defaultTags": ["#AI工具", "#AI教程", "#效率"]
        },
        "stats": {
            "totalPublished": 0,
            "totalViews": 0,
            "avgCompletionRate": 0
        }
    }
    path = PROJECT_ROOT / "accounts" / slug / "account.json"
    path.write_text(json.dumps(account, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ accounts/{slug}/account.json")


def migrate_topics(slug):
    """迁移选题库：知识赛道选题 → ai-tools-01，情感赛道暂存"""
    backlog_path = PROJECT_ROOT / "data" / "topics" / "backlog.json"
    if not backlog_path.exists():
        print("  ⚠ backlog.json 不存在，跳过选题迁移")
        return

    with open(backlog_path, encoding="utf-8") as f:
        backlog = json.load(f)

    # 知识赛道标签关键词
    knowledge_tags = {"OpenClaw", "养龙虾", "AI智能体", "AI工具", "豆包", "千问",
                      "DeepSeek", "ChatGPT", "AI副业", "免费AI", "效率工具",
                      "Suno", "AI音乐", "科技热点", "AI避坑", "热搜",
                      "AI替代", "国产AI", "赚钱", "副业收入", "办公提效", "工具推荐",
                      "AI翻唱", "音乐制作"}
    emotion_tags = {"人生感悟", "成长", "治愈", "自我提升", "心理学",
                    "社交心理", "朋友圈", "深度分析", "深夜", "情感语录", "正能量"}

    knowledge_topics = []
    emotion_topics = []

    for topic in backlog.get("topics", []):
        topic_tags = set(topic.get("tags", []))
        if topic_tags & emotion_tags:
            emotion_topics.append(topic)
        else:
            knowledge_topics.append(topic)

    # 为知识赛道选题补充路径信息
    content_mapping = {
        "topic-001": "2026-03-13-OpenClaw养龙虾科普",
        "topic-002": "2026-03-13-养虾避坑指南",
    }

    for topic in knowledge_topics:
        tid = topic["id"]
        if tid in content_mapping:
            name = content_mapping[tid]
            topic["scriptPath"] = f"content/scripts/{name}.md"
            topic["materialPath"] = f"content/materials/{name}/"
            topic["outputPath"] = f"content/output/{name}.mp4"
            topic["status"] = "material-ready"
        else:
            topic["scriptPath"] = None
            topic["materialPath"] = None
            topic["outputPath"] = None
        topic["publishId"] = None

    # 写入账号选题库
    account_topics = {
        "topics": knowledge_topics,
        "lastUpdated": TODAY,
        "nextId": max(int(t["id"].split("-")[1]) for t in knowledge_topics) + 1
        if knowledge_topics else 1
    }
    path = PROJECT_ROOT / "accounts" / slug / "topics.json"
    path.write_text(json.dumps(account_topics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ accounts/{slug}/topics.json ({len(knowledge_topics)} 个知识赛道选题)")

    # 情感赛道选题暂存
    if emotion_topics:
        pending = {
            "topics": emotion_topics,
            "note": "待创建情感赛道账号后分配",
            "lastUpdated": TODAY
        }
        pending_path = PROJECT_ROOT / "data" / "topics" / "pending-emotion.json"
        pending_path.write_text(json.dumps(pending, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  ✓ data/topics/pending-emotion.json ({len(emotion_topics)} 个情感赛道选题待分配)")

    # 备份旧文件
    backup_path = backlog_path.with_suffix(".json.bak")
    shutil.copy2(backlog_path, backup_path)
    print(f"  ✓ backlog.json 已备份为 backlog.json.bak")


def create_published_json(slug):
    """创建空的发布历史"""
    published = {"records": [], "lastUpdated": TODAY}
    path = PROJECT_ROOT / "accounts" / slug / "published.json"
    path.write_text(json.dumps(published, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ accounts/{slug}/published.json")


def migrate_content(slug):
    """移动现有内容到账号目录"""
    account_dir = PROJECT_ROOT / "accounts" / slug

    # 移动脚本
    src_scripts = PROJECT_ROOT / "content" / "scripts"
    dst_scripts = account_dir / "content" / "scripts"
    if src_scripts.exists():
        for f in src_scripts.glob("*.md"):
            dst = dst_scripts / f.name
            shutil.copy2(f, dst)
            print(f"  ✓ 脚本: {f.name} → accounts/{slug}/content/scripts/")

    # 移动素材
    src_materials = PROJECT_ROOT / "content" / "materials"
    dst_materials = account_dir / "content" / "materials"
    if src_materials.exists():
        for d in src_materials.iterdir():
            if d.is_dir():
                dst = dst_materials / d.name
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(d, dst)
                print(f"  ✓ 素材: {d.name}/ → accounts/{slug}/content/materials/")

    # 移动输出
    src_output = PROJECT_ROOT / "content" / "output"
    dst_output = account_dir / "content" / "output"
    if src_output.exists():
        for f in src_output.iterdir():
            if f.is_file():
                dst = dst_output / f.name
                shutil.copy2(f, dst)
                print(f"  ✓ 输出: {f.name} → accounts/{slug}/content/output/")


def cleanup_old_structure():
    """清理旧目录结构（保留空目录作为提示）"""
    old_dirs = [
        PROJECT_ROOT / "content" / "scripts",
        PROJECT_ROOT / "content" / "materials",
        PROJECT_ROOT / "content" / "output",
    ]
    for d in old_dirs:
        if d.exists():
            readme = d / "_MIGRATED.md"
            readme.write_text(
                f"# 已迁移\n\n此目录内容已迁移到 `accounts/` 下对应账号目录。\n"
                f"新内容请使用 `/account 切换 {{slug}}` 后操作。\n"
                f"迁移日期: {TODAY}\n",
                encoding="utf-8"
            )
    print("  ✓ 旧目录已标记迁移提示")


def main():
    slug = "ai-tools-01"

    print("=" * 50)
    print("抖音矩阵化架构迁移")
    print("=" * 50)

    print("\n[1/7] 创建矩阵注册表...")
    create_matrix_json()

    print("\n[2/7] 创建去重指纹库...")
    create_dedup_db()

    print("\n[3/7] 创建账号目录结构...")
    create_account_structure(slug)
    create_account_json(slug)

    print("\n[4/7] 迁移选题库...")
    migrate_topics(slug)

    print("\n[5/7] 创建发布历史...")
    create_published_json(slug)

    print("\n[6/7] 迁移现有内容...")
    migrate_content(slug)

    print("\n[7/7] 清理旧结构...")
    cleanup_old_structure()

    print(f"\n{'=' * 50}")
    print("迁移完成！")
    print(f"{'=' * 50}")
    print(f"\n账号 {slug} 已就绪。下一步：")
    print(f"  1. /account             — 查看账号列表")
    print(f"  2. /account 切换 {slug} — 开始使用")
    print(f"  3. /account 创建 healing-01 — 创建情感赛道账号")


if __name__ == "__main__":
    main()
