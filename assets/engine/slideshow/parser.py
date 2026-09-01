# -*- coding: utf-8 -*-
r"""
mdshow :: slideshow.parser
把 Markdown 讲稿解析成幻灯片模型（Slide / Block）。

支持两种方言，按「是否出现独立 --- 行」自动识别：

方言 A（人类讲稿，如 lect1/index.md）：
  # 标题        -> 封面页（全幅紫渐变）
  ## 标题       -> 内容页（紫渐变标题栏）
  ### 文本      -> 正文粗体小节句
  - 文本        -> 圆点列表项（默认分步显示，行尾 {nf} 关闭分步）
  - > 文本      -> 列表内 AIGC 卡（✦ 淡紫水印，等价于手写 <span class="aigc">）
  > 文本        -> 引用块（大引号 + 左竖线容器；内部可含 aigc span）
  [[描述]]      -> 图片占位卡（构建时输出警告，提醒补图）

方言 B（make-slides 技能产物，规范见 .agents/skills/make-slides/SKILL.md）：
  ---           -> 分页
  # 标题        -> 内容页标题栏（Title Case，每页一个）
  ## 标题       -> 页内小节标题（每页 1-2 个）
  - 文本        -> 圆点列表项
  ␠␠- 文本      -> 嵌套列表（缩进 ≥2 空格，随父项一同显示）
  <span class="aigc">文本</span> -> AI 生成水印（✦ 淡紫高亮，行内透传）
  > 文本        -> 引用块（多行连续 > 合并为同一块；内部 aigc span 照常透传）

通用行内语法：
  [文字](url) 链接 / **粗体** / *着重* / `代码` / ~~删除~~
  $...$ 行内数学 / $$...$$ 展示数学（轻量 TeX：命令映射 + ^{} _{} 上下标，
  支持 \mid \prod \sum \forall \approx \neq \times 等，非完整 TeX）
"""
import re


# 数学命令 -> Unicode 映射（长命令优先替换，避免 \in 吃掉 \infty）
# 注：\mid 用普通竖线 | 而非 U+2223 ∣——后者在 Times/Georgia 中缺字形，
# 浏览器回退渲染后观感近似斜杠（jyy 复刻实战教训）
MATH_CMD_MAP = {
    "\\mid": "|", "\\prod": "∏", "\\sum": "∑", "\\forall": "∀",
    "\\infty": "∞", "\\times": "×", "\\approx": "≈", "\\neq": "≠",
    "\\leq": "≤", "\\geq": "≥", "\\ldots": "…", "\\cdots": "⋯",
    "\\cup": "∪", "\\cap": "∩", "\\rightarrow": "→", "\\to": "→",
    "\\in": "∈", "\\%": "%",
}


# 拆开 sub/sup 标签，让标签内文本（下标变量）也走变量斜体规则
_TAG_SPLIT_RE = re.compile(r"(<(?:sub|sup)>[^<]*</(?:sub|sup)>)")
# 连续字母串：单字母 → 变量，多字母 → 标识符/函数名（保持正体）
_WORD_RE = re.compile(r"[A-Za-z]+")
# 紧贴字母数字/括号的竖线（| 无空格一侧补薄空格，留出条件竖线的气口）
# 左右两条独立规则；在上下标转换前执行（纯文本阶段），故前邻需含 }
_BAR_L_RE = re.compile(r"([A-Za-z0-9\)}])\|")
_BAR_R_RE = re.compile(r"\|([A-Za-z0-9\(\[{])")
# 薄空格（U+2009）：比普通空格窄，模拟 LaTeX 关系符间距
_THIN = "\u2009"


def _wrap_single_vars(text):
    """ISO 80000 / LaTeX 惯例：单字母变量斜体，多字母标识符正体。

    用 <var> 而非 <i>：v2 主题把 .slide-body i/em 映射为中文着重号
    （text-emphasis），数学里若用 <i> 会带着重号点，冲突。
    特例：O( 的大 O 是记号不是变量，保持正体。
    """
    text = text.replace("O(", "\x01(")          # 保护大 O 记号
    text = _WORD_RE.sub(
        lambda m: "<var>%s</var>" % m.group(0) if len(m.group(0)) == 1 else m.group(0),
        text)
    return text.replace("\x01(", "O(")


def render_math(expr):
    r"""轻量数学渲染：命令映射 + 上下标 + 变量斜体/标识符正体。

    输入已经过 esc()，此处插入的 <sub>/<sup>/<var> 标签是安全的。
    设计动机：jyy 原版 tu13 曾因未渲染的 LaTeX 源码裸露而翻车
    （“$P(x_{1:n}\mid c)=\prod_i...” 直接印在幻灯片上），本函数保证
    常用命令都能落到可读的 Unicode/HTML 上。

    v2 排版规则（修复“整体斜体像加粗英文”的刻意感）：
      - 单字母（x, n, c, s...）→ <var> 斜体，即数学变量惯例；
      - 多字母（Pr, token, concat, Base64...）保持正体，即函数名/标识符惯例；
      - 数字/运算符正体；条件竖线两侧补薄空格。
    """
    for cmd in sorted(MATH_CMD_MAP, key=len, reverse=True):
        expr = expr.replace(cmd, MATH_CMD_MAP[cmd])
    # 竖线气口：趁纯文本阶段先做（转出 sub/sup 标签后就难判断跨标签紧贴了）；
    # 哪侧无空格补哪侧，已有空格则不动
    expr = _BAR_L_RE.sub(r"\1" + _THIN + "|", expr)
    expr = _BAR_R_RE.sub("|" + _THIN + r"\1", expr)
    expr = re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", expr)
    expr = re.sub(r"\^\{([^}]+)\}", r"<sup>\1</sup>", expr)
    expr = re.sub(r"_([A-Za-z0-9])", r"<sub>\1</sub>", expr)
    expr = re.sub(r"\^([A-Za-z0-9])", r"<sup>\1</sup>", expr)
    # 分段处理：sub/sup 标签内文本也做变量斜体，标签外再做竖线气口
    parts = _TAG_SPLIT_RE.split(expr)
    for i, p in enumerate(parts):
        if not p:
            continue
        if p.startswith("<"):
            m = re.match(r"<(sub|sup)>(.*)</(?:sub|sup)>$", p, re.S)
            if m:
                parts[i] = "<%s>%s</%s>" % (
                    m.group(1), _wrap_single_vars(m.group(2)), m.group(1))
        else:
            parts[i] = _wrap_single_vars(p)
    return "".join(parts)


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
# 白名单透传：aigc 开闭标签 + 数学/公式常用上下标标签（严格字面匹配）
AIGC_TAG_RE = re.compile(
    r'<span\s+class="aigc"\s*>|</span\s*>|<sub>|</sub>|<sup>|</sup>',
    re.IGNORECASE,
)
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
    t = re.sub(r"~~([^~]+)~~", r"<del>\1</del>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    # 数学（先展示式后行内式，避免 $$ 被行内规则吃掉一半）
    t = MATH_DISP_RE.sub(
        lambda m: '<span class="math math-d">' + render_math(m.group(1)) + "</span>", t)
    t = MATH_INLINE_RE.sub(
        lambda m: '<span class="math">' + render_math(m.group(1)) + "</span>", t)
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

        # ---- 引用块（`>` 容器语义：借鉴 jyy 原版——引用是容器，
        #      AIGC 标记由内部 span 负责，两者正交；连续行合并为同一块） ----
        if s.startswith("> ") or s == ">":
            ensure_slide()
            body = s[2:] if len(s) > 1 else ""
            seg = parse_inline(body)
            if cur.blocks and cur.blocks[-1].kind == "quote":
                cur.blocks[-1].text += seg     # 连续引用行：中文直排拼接
            else:
                b = Block("quote")
                b.text = seg
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
    """统计分步元素个数（构建摘要用）。引用块随页直接显示，不计分步。"""
    n = 0
    for s in slides:
        for b in s.blocks:
            if b.kind == "ul":
                n += sum(1 for it in b.items if it["frag"])
    return n
