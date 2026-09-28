# douyin-drama-cover-kit

短视频影视剧解说号的封面与发布物料工具包。批量生成统一风格的系列封面（3:4 竖版 + 4:3 横版），配套标题/话题规范。题材无关——武侠、宫斗、悬疑、现代剧都能用。

## 效果

同一张系列底图，每集只换集数和两行四字标题：

- 顶部：剧名（小字行书）+ 第 X 集（大字行书）
- 底部：两行短标题（行书，与集数同字体）
- 上下渐变黑遮罩保证文字可读
- 同时输出 1080×1440（抖音/视频号竖版）和 1440×1080（B站/西瓜横版）

## 快速开始

### 1. 依赖
- Python 3.8+
- Pillow：`pip install pillow`
- ffmpeg（可选，仅抽帧用）

### 2. 配置
编辑 `scripts/make_covers.py` 顶部：
```python
BASE_IMAGE  = "path/to/your/series_base.jpg"
SERIES_NAME = "剧 名"
OUT_ROOT    = "."

EPS = [
    ("ep01", "cover_ep01.jpg", "第一集", "四字钩子", "四字钩子"),
    ("ep02", "cover_ep02.jpg", "第二集", "四字钩子", "四字钩子"),
]
```

### 3. 生成
```bash
python scripts/make_covers.py                # 两种比例都出
python scripts/make_covers.py --ratio 3x4    # 只要竖版
python scripts/make_covers.py --ratio 4x3    # 只要横版
```

## 目录结构

```
douyin-drama-cover-kit/
├── SKILL.md                      # 给 AI agent 看的触发与工作流说明
├── scripts/
│   ├── make_covers.py            # 批量封面生成
│   └── grab_frames.py            # 从原片批量抽候选帧
├── references/
│   └── publishing-guide.md       # 标题/话题/简介规范
└── assets/                       # 放你自己的底图
```

## 字体
自动跨平台检测：
- Windows：华文行楷 → 楷体 → 雅黑
- macOS：STKaiti → PingFang
- Linux：文泉驿 → Noto CJK

## 作为豆包 Skill 使用
把整个文件夹放到 `workspace/.user_skills/` 下，重启豆包即可。当你说"帮我给这系列剧做封面""批量生成抖音封面"时会自动触发。

## License
MIT
