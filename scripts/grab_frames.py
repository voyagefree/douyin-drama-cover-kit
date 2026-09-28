# -*- coding: utf-8 -*-
"""
从原片批量抽候选帧，拼成 contact sheet 供人工选图。

用法：
    python grab_frames.py --src-dir "E:\video\shediao" --out "E:\video\_frames"

约定：原片文件名为 01.mp4, 02.mp4, ...（两位数序号）。
每集解说对应的原片集数在 EPISODE_MAP 里配置。
"""
import argparse
import os
import subprocess
from PIL import Image

# 每集解说 -> 原片集数列表
# 例：{"ep1": [1], "ep2": [1, 2], "ep3": [2]}
EPISODE_MAP = {
    "ep1": [1],
    "ep2": [1, 2],
    "ep3": [2],
}

PERCENTS = [0.15, 0.35, 0.55, 0.75]
THUMB_W, THUMB_H = 480, 270
COLS = 2


def get_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    return float(r.stdout.strip())


def grab(src, t, out):
    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(t), "-i", src, "-frames:v", "1",
         "-q:v", "3", out],
        capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-dir", required=True, help="原片所在目录")
    ap.add_argument("--out", required=True, help="抽帧输出目录")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    for ep, srcs in EPISODE_MAP.items():
        frames = []
        for sn in srcs:
            path = os.path.join(args.src_dir, f"{sn:02d}.mp4")
            if not os.path.exists(path):
                print(f"skip missing: {path}")
                continue
            dur = get_duration(path)
            for pct in PERCENTS:
                t = dur * pct
                out = os.path.join(args.out, f"{ep}_s{sn}_p{int(pct*100)}.jpg")
                if not os.path.exists(out):
                    grab(path, t, out)
                frames.append(out)

        if not frames:
            continue
        imgs = [Image.open(f).resize((THUMB_W, THUMB_H)) for f in frames]
        rows = (len(imgs) + COLS - 1) // COLS
        sheet = Image.new("RGB", (THUMB_W * COLS, THUMB_H * rows), (20, 20, 20))
        for i, im in enumerate(imgs):
            sheet.paste(im, ((i % COLS) * THUMB_W, (i // COLS) * THUMB_H))
        sheet_path = os.path.join(args.out, f"sheet_{ep}.jpg")
        sheet.save(sheet_path, quality=85)
        print(f"OK: {sheet_path}  ({len(frames)} frames)")


if __name__ == "__main__":
    main()
