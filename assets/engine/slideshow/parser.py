# -*- coding: utf-8 -*-
"""
mdshow :: slideshow.parser
把 Markdown 讲稿解析成幻灯片模型（Slide / Block）。

支持两种方言，按「是否出现独立 --- 行」自动识别：

方言 A（人类讲稿，如 lect1/index.md）：
  # 标题        -> 封面页（全幅紫渐变）
  ## 标题       -> 内容页（紫渐变标题栏）
  ### 文本      -> 正文粗体小节句
  - 文本        -> 圆点列表项（默认分步显示，行尾 {nf} 关闭分步）
  - > 文本      -> 列表内 AIGC 卡（✦ 淡紫水印，等价于手写 <span class="aigc">）
  > 文本        -> 独立 AIGC 卡
  [[描述]]      -> 图片占位卡（构建时输出警告，提醒补图）

方言 B（make-slides 技能产物，规范见 .agents/skills/make-slides/SKILL.md）：
  ---           -> 分页
  # 标题        -> 内容页标题栏（Title Case，每页一个）
  ## 标题       -> 页内小节标题（每页 1-2 个）
  - 文本        -> 圆点列表项
  ␠␠- 文本      -> 嵌套列表（缩进 ≥2 空格，随父项一同显示）
  <span class="aigc">文本</span> -> AI 生成水印（✦ 淡紫高亮，行内透传）

通用行内语法：
  [文字](url) 链接 / **粗体** / *斜体* / `代码`
  $...$ 行内数学 / $$...$$ 展示数学（轻量排版，非完整 TeX）
"""
import re


class Block:
    """kind: 'h2' | 'h3' | 'p' | 'ul' | 'quote' | 'imgph' | 'mathd'"""

    def __init__(self, kind):
        self.kind = kind
        self.text = ""       # h2 / h3 / p / quote / imgph / mathd 用
        self.items = []      # ul 用：{text, callout, frag, depth}


class Slide:
    def __init__(self, level, title):
        self.level = level          # 1 = 封面(仅方言A), 2 = 内容页
        self.title = title
        self.blocks = []


PLACEHOLDER_RE = re.compile(r"\[\[([^\[\]]+)\]\]")
NF_MARKER_RE = re.compile(r"\s*\{nf\}\s*$")
AIGC_TAG_RE = re.compile(r'<span\s+class="aigc"\s*>|</span\s*>', re.IGNORECASE)
MATH_DISP_RE = re.compile(r"\$\$([^$\n]+)\$\$")
MATH_INLINE_RE = re.compile(r"\$([^$\n]+)\$")
ITEM_RE = re.compile(r"^(?:-|•)\s+(.*)$")


def esc(text):
    """HTML 转义（最先执行，之后所有 inline 规则都作用在转义后的文本上）"""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def parse_inline(text):
    """行内 Markdown -> HTML

    <span class="aigc"> 标签走白名单：先摘出暂存，转义后原样放回，
    使技能产物里的 AI 水印标记可以直接透传到最终 HTML。
    """
    stash = []

    def _keep(m):
        stash.append(m.group(0))
        return "\x00%d\x00" % (len(stash) - 1)

    t = AIGC_TAG_RE.sub(_keep, text)
    t = esc(t)
    t = re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    # 数学（先展示式后行内式，避免 $$ 被行内规则吃掉一半）
    t = MATH_DISP_RE.sub(r'<span class="math math-d">\1</span>', t)
    t = MATH_INLINE_RE.sub(r'<span class="math">\1</span>', t)
    # 行内图片占位符（整行 [[...]] 会在块级被先截获为占位卡）
    t = PLACEHOLDER_RE.sub(r'<span class="ph">\1</span>', t)
    return t


def parse(md_text):
    """Markdown 文本 -> (slides, placeholders, dialect_b)

    placeholders: [{"line": 行号(1-based), "text": 占位描述}, ...]
    dialect_b:    是否按方言 B 解析（存在独立 --- 行）
    """
    lines = md_text.splitlines()
    dialect_b = any(s.strip() == "---" for s in lines)

    slides = []
    placeholders = []
    cur = None
    prev_is_para = False   # 相邻物理行合并成同一段落

    def new_slide(level, title):
        nonlocal cur, prev_is_para
        cur = Slide(level, title)
        slides.append(cur)
        prev_is_para = False

    def ensure_slide():
        """方言 B：--- 之后若直接跟内容，开一个无标题内容页兜底"""
        nonlocal cur, prev_is_para
        if cur is None:
            cur = Slide(2, "")
            slides.append(cur)
        prev_is_para = False

    for lineno, raw in enumerate(lines, 1):
        line = raw.rstrip()
        s = line.strip()

        if not s:
            prev_is_para = False
            continue

        # ---- 方言 B：--- 分页 ----
        if dialect_b and s == "---":
            cur = None
            prev_is_para = False
            continue

        # ---- 标题族 ----
        if s.startswith("### "):
            ensure_slide()
            b = Block("h3")
            b.text = parse_inline(s[4:])
            cur.blocks.append(b)
            continue
        if s.startswith("## "):
            if dialect_b:
                ensure_slide()
                b = Block("h2")
                b.text = parse_inline(s[3:])
                cur.blocks.append(b)
            else:
                new_slide(2, s[3:])
            continue
        if s.startswith("# "):
            if dialect_b:
                new_slide(2, s[2:])    # 方言 B：# = 标题栏内容页
            else:
                new_slide(1, s[2:])    # 方言 A：# = 封面
            continue

        if cur is None:
            if dialect_b:
                ensure_slide()
            else:
                raise ValueError(
                    f"第 {lineno} 行：讲稿必须以 '# 封面标题' 或 '## 页标题' 开头"
                )

        # ---- 整行图片占位符 ----
        m = PLACEHOLDER_RE.fullmatch(s)
        if m:
            b = Block("imgph")
            b.text = parse_inline(m.group(1))
            cur.blocks.append(b)
            placeholders.append({"line": lineno, "text": m.group(1)})
            prev_is_para = False
            continue

        # ---- 展示数学（独立一行 $$...$$） ----
        m = re.fullmatch(r"\$\$(.+)\$\$", s)
        if m:
            b = Block("mathd")
            b.text = parse_inline(m.group(1))
            cur.blocks.append(b)
            prev_is_para = False
            continue

        # ---- AIGC 卡（独立） ----
        if s.startswith("> "):
            b = Block("quote")
            b.text = parse_inline(s[2:])
            cur.blocks.append(b)
            prev_is_para = False
            continue

        # ---- 列表（支持嵌套；"- > " 为列表内 AIGC 卡） ----
        m = ITEM_RE.match(s)
        if m:
            ensure_slide()
            item = m.group(1)
            depth = 1 if (len(line) - len(line.lstrip(" "))) >= 2 else 0
            if cur.blocks and cur.blocks[-1].kind == "ul":
                ul = cur.blocks[-1]
            else:
                ul = Block("ul")
                cur.blocks.append(ul)
            callout = item.startswith("> ")
            if callout:
                item = item[2:]
            frag = True
            if NF_MARKER_RE.search(item):   # 行尾 {nf} = 取消分步
                frag = False
                item = NF_MARKER_RE.sub("", item)
            ul.items.append({
                "text": parse_inline(item),
                "callout": callout,
                "frag": frag and depth == 0,   # 嵌套子项随父项显示，不单独分步
                "depth": depth,
            })
            prev_is_para = False
            continue

        # ---- 普通段落（相邻行合并） ----
        ensure_slide_para(prev_is_para, cur, s)
        prev_is_para = True

    if not slides:
        raise ValueError("讲稿为空：至少需要一个 '# ' 或 '## ' 标题（方言 B 需以 '# ' 开头）")

    return slides, placeholders, dialect_b


def ensure_slide_para(prev_is_para, cur, s):
    """段落的合并/新建（拆出小函数只为可读性）"""
    if prev_is_para and cur.blocks and cur.blocks[-1].kind == "p":
        cur.blocks[-1].text += s            # 中文直排，不加空格
    else:
        b = Block("p")
        b.text = parse_inline(s)
        cur.blocks.append(b)


def count_fragments(slides):
    """统计分步元素个数（构建摘要用）"""
    n = 0
    for s in slides:
        for b in s.blocks:
            if b.kind == "ul":
                n += sum(1 for it in b.items if it["frag"])
            elif b.kind == "quote":
                n += 1
    return n
