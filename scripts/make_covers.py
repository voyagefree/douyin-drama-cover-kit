# -*- coding: utf-8 -*-
"""
批量生成抖音剧集解说封面：统一底图 + 行书集数 + 短标题。
同时输出 3:4 竖版和 4:3 横版（可选）。

用法：
    python make_covers.py                # 两种比例都出
    python make_covers.py --ratio 3x4    # 只出竖版
    python make_covers.py --ratio 4x3    # 只出横版

使用前修改下方 CONFIG 区：
    BASE_IMAGE  : 系列统一底图路径
    SERIES_NAME : 系列名（如"甄嬛传"）
    OUT_ROOT    : 输出根目录
    EPS         : 每集配置列表
"""
import argparse
import os
import sys
from PIL import Image, ImageDraw, ImageFont

# ============ CONFIG ============
BASE_IMAGE = "path/to/your/series_base.jpg"   # TODO: 换成你的系列底图
SERIES_NAME = "剧 名"                           # TODO: 换成你的剧名
OUT_ROOT = "."                                  # TODO: 输出根目录

# 每集：(输出子目录, 文件名, 集数大字, 标题行1, 标题行2)
# 标题每行建议 4 字，网感优先（见 references/publishing-guide.md）
EPS = [
    ("ep00", "cover_pilot.jpg",   "先 导",  "一口气",  "看完开局"),
    ("ep01", "cover_ep01.jpg",    "第一集", "四字钩子", "四字钩子"),
    ("ep02", "cover_ep02.jpg",    "第二集", "四字钩子", "四字钩子"),
]
# ================================


def find_font(candidates_by_platform, size):
    """跨平台找可用字体。"""
    if sys.platform == "win32":
        paths = candidates_by_platform.get("win", [])
    elif sys.platform == "darwin":
        paths = candidates_by_platform.get("mac", [])
    else:
        paths = candidates_by_platform.get("linux", [])
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    # 最后回退到默认字体
    print(f"[warn] no preferred font found, using default", file=sys.stderr)
    return ImageFont.load_default(size=size)


FONT_CHINESE = {
    "win": [
        r"C:\Windows\Fonts\STXINGKA.TTF",   # 华文行楷
        r"C:\Windows\Fonts\simkai.ttf",      # 楷体
        r"C:\Windows\Fonts\msyhbd.ttc",      # 雅黑粗体
    ],
    "mac": [
        "/System/Library/Fonts/STKaiti.ttf",
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/Songti.ttc",
    ],
    "linux": [
        "/usr/share/fonts/truetype/arphic/uming.ttc",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
}


def center(draw, y, text, font, color, W):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((W - w) // 2, y), text, font=font, fill=color)


def cover_crop(frame, W, H):
    fw, fh = frame.size
    target_ratio = W / H
    src_ratio = fw / fh
    if src_ratio > target_ratio:
        new_w = int(fh * target_ratio)
        x0 = (fw - new_w) // 2
        frame = frame.crop((x0, 0, x0 + new_w, fh))
    else:
        new_h = int(fw / target_ratio)
        y0 = (fh - new_h) // 2
        frame = frame.crop((0, y0, fw, y0 + new_h))
    return frame.resize((W, H), Image.LANCZOS)


def make_one(out_path, base, W, H, series, ep_label, t1, t2):
    if H > W:  # 竖版 3:4
        f_series = find_font(FONT_CHINESE, 72)
        f_ep = find_font(FONT_CHINESE, 170)
        f_title = find_font(FONT_CHINESE, 78)
        top_h, bot_h = 560, 440
        y_series, y_ep = 90, 200
        y_t1, y_t2 = H - 260, H - 160
    else:      # 横版 4:3
        f_series = find_font(FONT_CHINESE, 56)
        f_ep = find_font(FONT_CHINESE, 120)
        f_title = find_font(FONT_CHINESE, 56)
        top_h, bot_h = 340, 280
        y_series, y_ep = 40, 120
        y_t1, y_t2 = H - 200, H - 120

    canvas = cover_crop(base, W, H)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(0, top_h):
        alpha = int(215 * (1 - y / top_h))
        od.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    for y in range(H - bot_h, H):
        alpha = int(225 * ((y - (H - bot_h)) / bot_h))
        od.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(canvas)
    center(draw, y_series, series, f_series, (255, 255, 255), W)
    center(draw, y_ep, ep_label, f_ep, (255, 255, 255), W)
    center(draw, y_t1, t1, f_title, (255, 255, 255), W)
    center(draw, y_t2, t2, f_title, (255, 255, 255), W)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    canvas.save(out_path, "JPEG", quality=92)
    print(f"OK: {out_path}")


def main():
    ap = argparse.ArgumentParser(description="Generate series covers for short-video platforms.")
    ap.add_argument("--ratio", choices=["3x4", "4x3", "both"], default="both")
    ap.add_argument("--base", default=BASE_IMAGE, help="Series base image path")
    ap.add_argument("--series", default=SERIES_NAME, help="Series name shown on cover")
    ap.add_argument("--out", default=OUT_ROOT, help="Output root directory")
    args = ap.parse_args()

    if not os.path.exists(args.base):
        sys.exit(f"[error] base image not found: {args.base}\n"
                 f"Edit BASE_IMAGE at the top of this script or pass --base.")

    base = Image.open(args.base).convert("RGB")
    sizes = []
    if args.ratio in ("3x4", "both"):
        sizes.append(("3x4", 1080, 1440))
    if args.ratio in ("4x3", "both"):
        sizes.append(("4x3", 1440, 1080))

    for subdir, fname, ep_label, t1, t2 in EPS:
        stem, ext = os.path.splitext(fname)
        for tag, W, H in sizes:
            out_name = f"{stem}_{tag}{ext}"
            out_path = os.path.join(args.out, subdir, out_name)
            make_one(out_path, base, W, H, args.series, ep_label, t1, t2)


if __name__ == "__main__":
    main()
