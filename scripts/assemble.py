#!/usr/bin/env python3
"""
视频自动组装脚本

用法:
    python scripts/assemble.py content/materials/2026-03-13-OpenClaw养龙虾科普/

功能: TTS配音 → 图片动效 → 字幕烧录 → BGM混音 → 导出成品MP4
"""

import subprocess
import sys
import re
import os
import shutil
import tempfile
from pathlib import Path


# ── 配置 ──────────────────────────────────────────────

TTS_VOICE = "zh-CN-YunxiNeural"
TTS_RATE = "+10%"
OUTPUT_WIDTH = 1080
OUTPUT_HEIGHT = 1920
FPS = 30
FADE_DURATION = 0.3  # 转场叠化秒数
BGM_VOLUME = 0.25    # BGM 相对音量

# 场景时间比例 (秒)，总计 90 秒
SCENE_RATIOS = [3, 12, 15, 15, 15, 15, 15]

# 场景图片文件名 (按顺序)
SCENE_FILES = [
    "scene-00-hook",
    "scene-01-what",
    "scene-02-capabilities",
    "scene-03-why-popular",
    "scene-04-how-to-use",
    "scene-05-risks",
    "scene-06-endcard",
]

# Ken Burns 动效配置: (start_zoom, end_zoom, pan_direction)
# pan_direction: "center", "up", "down"
SCENE_EFFECTS = [
    (1.0, 1.15, "center"),   # 场景0: 快速放大
    (1.0, 1.08, "up"),       # 场景1: 缓慢上移+放大
    (1.0, 1.08, "center"),   # 场景2: 缓慢放大
    (1.1, 1.0, "center"),    # 场景3: 缓慢缩小
    (1.0, 1.08, "up"),       # 场景4: 缓慢上移
    (1.0, 1.03, "center"),   # 场景5: 微幅（模拟微抖）
    (1.0, 1.0, "center"),    # 场景6: 静态
]


# ── 工具检查 ──────────────────────────────────────────

def check_dependencies():
    """检查 edge-tts 和 ffmpeg 是否可用"""
    missing = []

    if shutil.which("edge-tts") is None:
        missing.append("edge-tts  →  pip install edge-tts")

    if shutil.which("ffmpeg") is None:
        missing.append("ffmpeg    →  apt install ffmpeg / brew install ffmpeg")

    if shutil.which("ffprobe") is None:
        missing.append("ffprobe   →  随 ffmpeg 一起安装")

    if missing:
        print("缺少依赖，请先安装：")
        for m in missing:
            print(f"  {m}")
        sys.exit(1)


# ── TTS 生成 ──────────────────────────────────────────

def clean_tts_text(text: str) -> str:
    """去掉 TTS 文本中的标记，保留纯文本"""
    # 去掉【xxx】标记
    text = re.sub(r'【[^】]+】', '', text)
    # 去掉单独的 ... 行（仅含省略号和空白的行）
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped == '...' or stripped == '':
            continue
        # 行内的 ... 替换为短停顿（逗号足矣，edge-tts 会自然停顿）
        line = line.replace('...', '，')
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)


def generate_tts(material_dir: Path) -> Path:
    """生成 TTS 配音文件"""
    tts_text_path = material_dir / "tts-text.txt"
    audio_dir = material_dir / "audio"
    audio_dir.mkdir(exist_ok=True)
    output_path = audio_dir / "voiceover.mp3"

    if output_path.exists():
        print(f"  配音已存在，跳过: {output_path}")
        return output_path

    if not tts_text_path.exists():
        print(f"错误: 找不到 {tts_text_path}")
        sys.exit(1)

    raw_text = tts_text_path.read_text(encoding='utf-8')
    clean_text = clean_tts_text(raw_text)

    # 写入临时文件供 edge-tts 使用
    tmp_text = material_dir / "audio" / "_tts_clean.txt"
    tmp_text.write_text(clean_text, encoding='utf-8')

    print("  正在生成 TTS 配音...")
    cmd = [
        "edge-tts",
        "--voice", TTS_VOICE,
        "--rate", TTS_RATE,
        "--file", str(tmp_text),
        "--write-media", str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  TTS 生成失败: {result.stderr}")
        sys.exit(1)

    tmp_text.unlink(missing_ok=True)
    print(f"  配音已生成: {output_path}")
    return output_path


# ── 音频工具 ──────────────────────────────────────────

def get_duration(file_path: Path) -> float:
    """用 ffprobe 获取音视频时长（秒）"""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def calculate_scene_durations(total_duration: float) -> list[float]:
    """按比例分配每个场景的时长"""
    ratio_sum = sum(SCENE_RATIOS)
    return [total_duration * r / ratio_sum for r in SCENE_RATIOS]


# ── 图片查找 ──────────────────────────────────────────

def find_scene_image(images_dir: Path, scene_name: str) -> Path | None:
    """查找场景图片，支持 png/jpg/webp"""
    for ext in ["png", "jpg", "jpeg", "webp"]:
        p = images_dir / f"{scene_name}.{ext}"
        if p.exists():
            return p
    return None


# ── Ken Burns 视频片段生成 ────────────────────────────

def create_scene_clip(
    image_path: Path,
    duration: float,
    effect: tuple,
    output_path: Path,
    is_first: bool = False,
    is_last: bool = False,
):
    """用 FFmpeg zoompan 为单张图片生成带动效的视频片段"""
    start_zoom, end_zoom, pan_dir = effect
    total_frames = int(duration * FPS)

    if total_frames < 1:
        total_frames = 1

    # zoompan 参数
    # zoom: 从 start_zoom 线性变化到 end_zoom
    if start_zoom == end_zoom:
        zoom_expr = f"{start_zoom}"
    else:
        zoom_expr = f"{start_zoom}+({end_zoom}-{start_zoom})*on/{total_frames}"

    # pan: 根据方向设置 x, y
    # zoompan 输出尺寸 = 输入尺寸 / zoom，所以 pan 范围是 (输入-输出)/2
    if pan_dir == "up":
        # 从下往上平移
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = f"ih/2-(ih/zoom/2)-({0.05}*ih*on/{total_frames})"
    elif pan_dir == "down":
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = f"ih/2-(ih/zoom/2)+({0.05}*ih*on/{total_frames})"
    else:  # center
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"

    # 构建 filter_complex
    filters = []

    # 1. 缩放输入图片到足够大的尺寸供 zoompan 使用
    filters.append(f"scale={OUTPUT_WIDTH * 2}:{OUTPUT_HEIGHT * 2}:flags=lanczos")

    # 2. zoompan 动效
    filters.append(
        f"zoompan=z='{zoom_expr}'"
        f":x='{x_expr}':y='{y_expr}'"
        f":d={total_frames}:s={OUTPUT_WIDTH}x{OUTPUT_HEIGHT}"
        f":fps={FPS}"
    )

    # 3. 确保像素格式
    filters.append("format=yuv420p")

    # 4. 叠化 fade
    fade_frames = int(FADE_DURATION * FPS)
    fade_parts = []
    if not is_first:
        fade_parts.append(f"fade=t=in:st=0:d={FADE_DURATION}")
    if not is_last:
        fade_out_start = duration - FADE_DURATION
        if fade_out_start < 0:
            fade_out_start = 0
        fade_parts.append(f"fade=t=out:st={fade_out_start}:d={FADE_DURATION}")

    if fade_parts:
        filters.append(",".join(fade_parts))

    filter_str = ",".join(filters)

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-vf", filter_str,
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    FFmpeg 错误: {result.stderr[-500:]}")
        sys.exit(1)


# ── 视频组装 ──────────────────────────────────────────

def assemble_video(material_dir: Path):
    """完整组装流程"""
    images_dir = material_dir / "images"
    audio_dir = material_dir / "audio"
    srt_path = material_dir / "subtitles.srt"
    bgm_path = audio_dir / "bgm.mp3"

    # 确定输出路径
    dir_name = material_dir.name  # 如 "2026-03-13-OpenClaw养龙虾科普"
    output_dir = material_dir.parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"{dir_name}.mp4"

    # 检查图片
    print("\n[1/5] 检查场景图片...")
    scene_images = []
    missing = []
    for name in SCENE_FILES:
        img = find_scene_image(images_dir, name)
        if img:
            scene_images.append(img)
            print(f"  ✓ {img.name}")
        else:
            missing.append(name)
            print(f"  ✗ {name}.png (缺失)")

    if missing:
        print(f"\n缺少 {len(missing)} 张图片，请先生成后放入 {images_dir}/")
        print("文件名格式: scene-XX-xxx.png (支持 png/jpg/webp)")
        sys.exit(1)

    # TTS 配音
    print("\n[2/5] 生成 TTS 配音...")
    voiceover_path = generate_tts(material_dir)
    total_duration = get_duration(voiceover_path)
    print(f"  配音时长: {total_duration:.1f} 秒")

    # 计算场景时长
    durations = calculate_scene_durations(total_duration)
    print("\n[3/5] 生成场景视频片段（Ken Burns 动效）...")
    for i, (img, dur) in enumerate(zip(scene_images, durations)):
        print(f"  场景{i}: {img.name} ({dur:.1f}s)")

    # 生成各场景视频片段
    tmp_dir = Path(tempfile.mkdtemp(prefix="douyin_assemble_"))
    clip_paths = []

    for i, (img, dur, effect) in enumerate(zip(scene_images, durations, SCENE_EFFECTS)):
        clip_path = tmp_dir / f"clip_{i:02d}.mp4"
        print(f"  正在处理场景{i}...", end=" ", flush=True)
        create_scene_clip(
            img, dur, effect, clip_path,
            is_first=(i == 0),
            is_last=(i == len(scene_images) - 1),
        )
        clip_paths.append(clip_path)
        print("✓")

    # 拼接所有片段
    print("\n[4/5] 拼接视频 + 配音 + 字幕...")
    concat_list = tmp_dir / "concat.txt"
    with open(concat_list, 'w') as f:
        for cp in clip_paths:
            f.write(f"file '{cp}'\n")

    # 先拼接视频
    concat_video = tmp_dir / "concat.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        str(concat_video),
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True)

    # 构建最终命令：视频 + 配音 + 字幕 + (可选)BGM
    print("  添加配音和字幕...")

    inputs = ["-i", str(concat_video), "-i", str(voiceover_path)]
    filter_parts = []
    audio_map = "[1:a]"

    # 字幕滤镜
    if srt_path.exists():
        # 转义路径中的特殊字符给 FFmpeg subtitles 滤镜
        srt_escaped = str(srt_path).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        subtitle_filter = (
            f"subtitles='{srt_escaped}'"
            f":force_style='FontSize=20,PrimaryColour=&HFFFFFF&"
            f",OutlineColour=&H000000&,Outline=2"
            f",MarginV=80,Alignment=2'"
        )
        filter_parts.append(subtitle_filter)
    else:
        print("  (字幕文件不存在，跳过)")

    # BGM 混音
    has_bgm = bgm_path.exists()
    if has_bgm:
        print("  混合 BGM...")
        inputs.extend(["-i", str(bgm_path)])
        # 配音 100% + BGM 25%，以配音长度为准
        audio_map = None  # 用 filter_complex 处理
    else:
        print("  (无 BGM 文件，跳过)")

    # 组装最终命令
    cmd = ["ffmpeg", "-y"] + inputs

    if has_bgm:
        # 音频混合
        audio_filter = (
            f"[1:a]volume=1.0[voice];"
            f"[2:a]volume={BGM_VOLUME}[bgm];"
            f"[voice][bgm]amix=inputs=2:duration=first[aout]"
        )
        if filter_parts:
            video_filter = ",".join(filter_parts)
            cmd += ["-filter_complex", f"{audio_filter}", "-vf", video_filter]
        else:
            cmd += ["-filter_complex", audio_filter]
        cmd += ["-map", "0:v", "-map", "[aout]"]
    else:
        if filter_parts:
            cmd += ["-vf", ",".join(filter_parts)]
        cmd += ["-map", "0:v", "-map", "1:a"]

    cmd += [
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  最终合成失败: {result.stderr[-800:]}")
        # 清理临时文件
        shutil.rmtree(tmp_dir, ignore_errors=True)
        sys.exit(1)

    # 清理临时文件
    print("\n[5/5] 清理临时文件...")
    shutil.rmtree(tmp_dir, ignore_errors=True)

    # 输出结果
    final_duration = get_duration(output_path)
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"\n{'='*50}")
    print(f"成品已生成!")
    print(f"  文件: {output_path}")
    print(f"  时长: {final_duration:.1f} 秒")
    print(f"  大小: {file_size_mb:.1f} MB")
    print(f"{'='*50}")
    print(f"\n下一步: 将视频上传到抖音，发布信息见 content/output/{dir_name}-meta.md")


# ── 入口 ──────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/assemble.py <素材目录>")
        print("示例: python scripts/assemble.py content/materials/2026-03-13-OpenClaw养龙虾科普/")
        sys.exit(1)

    material_dir = Path(sys.argv[1]).resolve()
    if not material_dir.is_dir():
        print(f"错误: 目录不存在 {material_dir}")
        sys.exit(1)

    print(f"视频自动组装")
    print(f"素材目录: {material_dir.name}")
    print(f"{'='*50}")

    check_dependencies()
    assemble_video(material_dir)


if __name__ == "__main__":
    main()
