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
  ␣␣- 文本      -> 嵌套列表（缩进 ≥2 空格，随父项一同显示）
  - > 文本      -> 列表内 AIGC 卡（✦ 淡紫水印，等价于手写 <span class="aigc">）
  - [ ] / - [x] -> 任务列表（☐ / ☑，分步规则同普通列表）
  1. 文本       -> 有序列表（start 取首项号，分步规则同无序列表）
  > 文本        -> 引用块（大引号 + 左竖线容器；内部可含 aigc span）
  | 表格行 |     -> 表格（下一行需为 |---|---| 分隔行，支持 :---: 对齐）
  ```lang       -> 围栏代码块（到闭围栏为止，内容原样转义不解析）
  ![说明](url)  -> 真实图片（整行则居中图版；行内则小图内联）
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
  [文字](url) 链接 / **粗体** / ***粗斜体*** / *着重* / ~~删除~~
  `代码`（最先解析：内容不再参与后续规则，标准 Markdown 行为）
  ![说明](url) 行内图片
  $...$ 行内数学 / $$...$$ 展示数学（轻量 TeX：命令映射 + ^{} _{} 上下标 +
  \sqrt{...}，支持 \mid \prod \sum \forall \log \sin 等函数名与常用符号，
  非完整 TeX）

方言识别注意：预扫独立 --- 行时会跳过围栏代码块内的行，
因此代码块里写 --- 不会把整篇翻转成方言 B。
"""
import re


# 数学命令 -> Unicode 映射（长命令优先替换，避免 \in 吃掉 \infty、\log 吃掉 \lg）
# 注：\mid 用普通竖线 | 而非 U+2223 ∣——后者在 Times/Georgia 中缺字形，
# 浏览器回退渲染后观感近似斜杠（jyy 复刻实战教训）
# 函数名类（2026-09 补）：映射为多字母正体文本——_wrap_single_vars 只斜体化
# 单字母，多字母自动保持函数名正体惯例；若不映射，LaTeX 命令会字面裸露
# （A4 规则：宁可少写公式，不可裸奔源码。实战踩坑：$O(n \log n)$ 的 \log）
MATH_CMD_MAP = {
    "\\mid": "|", "\\prod": "∏", "\\sum": "∑", "\\forall": "∀",
    "\\infty": "∞", "\\times": "×", "\\approx": "≈", "\\neq": "≠",
    "\\leq": "≤", "\\geq": "≥", "\\ldots": "…", "\\cdots": "⋯",
    "\\cup": "∪", "\\cap": "∩", "\\rightarrow": "→", "\\to": "→",
    "\\in": "∈", "\\%": "%", "\\pm": "±", "\\cdot": "·",
    "\\log": "log", "\\ln": "ln", "\\lg": "lg", "\\exp": "exp",
    "\\sin": "sin", "\\cos": "cos", "\\tan": "tan",
    "\\max": "max", "\\min": "min", "\\lim": "lim",
    "\\gcd": "gcd", "\\det": "det",
}
# \sqrt{...} -> √(...)：带参命令不适合命令表（参数含 {} 需整体捕获），
# 单独正则处理；捕获组允许"一层花括号嵌套"（\sqrt{x_{1}} 的下标），
# 两层以上嵌套仍不支持（轻量实现的已知边界）。
# 注意不能用非贪婪 .+?：\sqrt{x_{1}} 会抢到最近的 } 捕获出 x_{1 半截
MATH_SQRT_RE = re.compile(r"\\sqrt\{((?:[^{}]|\{[^{}]*\})+)\}")


# 表格：分隔行 |---|---:|:---:|（至少两个短横，容许两侧无外竖线）
TABLE_SEP_RE = re.compile(
    r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?$")
# 真实图片 ![alt](src)：src 不含空白与右括号
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
# 有序列表项：1. / 1) 前缀（限三位数防误伤年份行）
OL_ITEM_RE = re.compile(r"^(\d{1,3})[.)]\s+(.*)$")
# 任务列表前缀：- [ ] 未完成 / - [x] 已完成（标记后需空格）
TASK_RE = re.compile(r"^\[( |x|X)\]\s+")
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
      - 数字/运算符正体；条件竖线两侧补薄空格；\sqrt{x} → √(x)。
    """
    for cmd in sorted(MATH_CMD_MAP, key=len, reverse=True):
        expr = expr.replace(cmd, MATH_CMD_MAP[cmd])
    # \sqrt{...}：先于上下标处理（参数内的 _{}^{} 留给后面的规则转）
    expr = MATH_SQRT_RE.sub(r"√(\1)", expr)
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
    """kind: 'h2' | 'h3' | 'p' | 'ul' | 'ol' | 'quote' | 'imgph' | 'mathd'
              | 'table' | 'code' | 'img'"""

    def __init__(self, kind):
        self.kind = kind
        self.text = ""       # h2 / h3 / p / quote / imgph / mathd / code（已转义）
        self.items = []      # ul / ol 用：{text, callout, frag, depth, task}
        self.header = []     # table 表头单元格
        self.rows = []       # table 数据行（每行为单元格列表）
        self.aligns = []     # table 对齐：'l'|'c'|'r'（按列）
        self.lang = ""       # code 围栏语言标注
        self.src = ""        # img 图片地址
        self.alt = ""        # img 说明文字
        self.start = 1       # ol 首项序号（start 属性）


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


def _split_table_row(s):
    """表格行 -> 单元格列表（去掉首尾外竖线后按 | 切分；不支持转义竖线）"""
    s = s.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def _parse_table_aligns(sep_line):
    """分隔行 -> 对齐标记列表：:---: 居中 / ---: 右 / 其余左"""
    out = []
    for c in _split_table_row(sep_line):
        left, right = c.startswith(":"), c.endswith(":")
        out.append("c" if left and right else "r" if right else "l")
    return out


def parse_inline(text):
    """行内 Markdown -> HTML

    <span class="aigc"> 标签走白名单：先摘出暂存，转义后原样放回，
    使技能产物里的 AI 水印标记可以直接透传到最终 HTML。

    解析顺序（2026-09 第三轮修订）：行内代码最先暂存（标准 Markdown
    行为：代码内容不参与后续规则，`**x**` 展示语法不再被吃掉）；
    粗斜体在粗体之前；代码占位在数学/占位符之后还原。
    """
    stash = []

    def _keep(m):
        stash.append(m.group(0))
        return "\x00%d\x00" % (len(stash) - 1)

    t = AIGC_TAG_RE.sub(_keep, text)
    t = esc(t)
    t = re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], t)
    # 行内代码最先暂存：内容冻结，不参与链接/强调/数学等规则
    codes = []

    def _stash_code(m):
        codes.append(m.group(1))
        return "\x02%d\x02" % (len(codes) - 1)

    t = re.sub(r"`([^`]+)`", _stash_code, t)
    # 行内真实图片：必须在链接规则之前（否则 [alt](src) 被链接规则先吃掉感叹号）
    t = IMG_RE.sub(
        lambda m: '<img class="inline-img" src="%s" alt="%s" loading="lazy">'
        % (m.group(2), m.group(1).replace('"', "&quot;")), t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*\*([^*]+)\*\*\*", r"<b><i>\1</i></b>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"~~([^~]+)~~", r"<del>\1</del>", t)
    # 数学（先展示式后行内式，避免 $$ 被行内规则吃掉一半）
    t = MATH_DISP_RE.sub(
        lambda m: '<span class="math math-d">' + render_math(m.group(1)) + "</span>", t)
    t = MATH_INLINE_RE.sub(
        lambda m: '<span class="math">' + render_math(m.group(1)) + "</span>", t)
    # 行内图片占位符（整行 [[...]] 会在块级被先截获为占位卡）
    t = PLACEHOLDER_RE.sub(r'<span class="ph">\1</span>', t)
    # 还原代码占位
    t = re.sub(r"\x02(\d+)\x02", lambda m: "<code>%s</code>" % codes[int(m.group(1))], t)
    return t


def parse(md_text):
    """Markdown 文本 -> (slides, placeholders, dialect_b)

    placeholders: [{"line": 行号(1-based), "text": 占位描述}, ...]
    dialect_b:    是否按方言 B 解析（存在独立 --- 行）
    """
    lines = md_text.splitlines()
    # 方言预扫：独立 --- 行 -> 方言 B。
    # 必须跳过围栏代码块内的行，否则代码示例里写 --- 会误翻全篇方言。
    dialect_b = False
    _fence = False
    for _s in lines:
        _st = _s.strip()
        if _st.startswith("```"):
            _fence = not _fence
            continue
        if not _fence and _st == "---":
            dialect_b = True
            break

    slides = []
    placeholders = []
    cur = None
    prev_is_para = False   # 相邻物理行合并成同一段落
    in_code = False        # 围栏代码块状态
    code_buf = []
    code_lang = ""
    in_table = False       # 表格数据行收集状态
    tab_block = None

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

        # ---- 围栏代码块（状态机最优先：内容不做任何解析）----
        if in_code:
            if s.startswith("```"):
                ensure_slide()
                b = Block("code")
                b.text = esc("\n".join(code_buf))
                b.lang = code_lang.replace('"', "")
                cur.blocks.append(b)
                in_code = False
                code_buf = []
                prev_is_para = False
            else:
                code_buf.append(line)      # 保留原始缩进
            continue
        if s.startswith("```"):
            in_code = True
            code_lang = s[3:].strip()
            code_buf = []
            prev_is_para = False
            continue

        # ---- 表格数据行收尾（表头/分隔行已在下方触发收集）----
        if in_table:
            if s and "|" in s:
                if not TABLE_SEP_RE.match(s):   # 分隔行不重复收集
                    tab_block.rows.append(_split_table_row(s))
                continue
            in_table = False               # 非表格行：落盘后照常处理本行

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

        # ---- 表格触发：当前行含 | 且下一物理行是分隔行 ----
        if "|" in s and lineno < len(lines) \
                and TABLE_SEP_RE.match(lines[lineno].strip()):
            ensure_slide()
            tab_block = Block("table")
            tab_block.header = _split_table_row(s)
            tab_block.aligns = _parse_table_aligns(lines[lineno].strip())
            cur.blocks.append(tab_block)
            in_table = True
            prev_is_para = False
            continue

        # ---- 整行真实图片 -> 居中图版 ----
        m = IMG_RE.fullmatch(s)
        if m:
            b = Block("img")
            b.alt = m.group(1).replace('"', "&quot;")
            b.src = m.group(2)
            cur.blocks.append(b)
            prev_is_para = False
            continue

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
        # 2026-09 修复：曾误用 parse_inline——进入前 $$ 定界符已被剥掉，
        # 而 parse_inline 的数学规则按 $ 定界匹配，永远无法命中，
        # 结果 LaTeX 源码（_{1:n}、\prod 等）原样裸奔（A4 事故的管线版）。
        # 展示块语义就是纯数学：esc + render_math 全管线渲染。
        m = re.fullmatch(r"\$\$(.+)\$\$", s)
        if m:
            b = Block("mathd")
            b.text = render_math(esc(m.group(1)))
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

        # ---- 列表（无序/有序，支持嵌套；"- > " 为列表内 AIGC 卡） ----
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
            task = None                     # None=普通项 / False=未完成 / True=完成
            if not callout:
                tm = TASK_RE.match(item)
                if tm:
                    task = tm.group(1).lower() == "x"
                    item = item[tm.end():]
            frag = True
            if NF_MARKER_RE.search(item):   # 行尾 {nf} = 取消分步
                frag = False
                item = NF_MARKER_RE.sub("", item)
            ul.items.append({
                "text": parse_inline(item),
                "callout": callout,
                "frag": frag and depth == 0,   # 嵌套子项随父项显示，不单独分步
                "depth": depth,
                "task": task,
            })
            prev_is_para = False
            continue

        # ---- 有序列表（1. / 1) 前缀；start 取首项号，分步规则同无序） ----
        mo = OL_ITEM_RE.match(s)
        if mo:
            ensure_slide()
            depth = 1 if (len(line) - len(line.lstrip(" "))) >= 2 else 0
            if cur.blocks and cur.blocks[-1].kind == "ol":
                ol = cur.blocks[-1]
            else:
                ol = Block("ol")
                ol.start = int(mo.group(1))
                cur.blocks.append(ol)
            frag = True
            item = mo.group(2)
            if NF_MARKER_RE.search(item):
                frag = False
                item = NF_MARKER_RE.sub("", item)
            ol.items.append({
                "text": parse_inline(item),
                "callout": False,
                "frag": frag and depth == 0,
                "depth": depth,
                "task": None,
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
            if b.kind in ("ul", "ol"):
                n += sum(1 for it in b.items if it["frag"])
    return n
