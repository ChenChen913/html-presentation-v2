# -*- coding: utf-8 -*-
"""
mdshow :: slideshow.render
幻灯片模型 -> 单文件 HTML（内联主题 CSS 与放映 JS）。
"""
from .parser import parse_inline

TEMPLATE = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="mdshow">
<title>__TITLE__</title>
<style>
__THEME__
</style>
</head>
<body>
<div class="viewport" id="viewport">
  <div class="stage" id="stage">
__SLIDES__
  </div>
</div>
<div class="helpbar" id="helpbar">←/→ 翻页 · 空格 下一步 · O 总览 · F 全屏 · 点击左右半屏翻页</div>
<script>
__RUNTIME__
</script>
</body>
</html>
"""


def render_cover(slide):
    parts = [f"<h1>{parse_inline(slide.title)}</h1>"]
    for b in slide.blocks:
        if b.kind == "p":
            parts.append(f'<p class="cover-sub">{b.text}</p>')
    return "".join(parts)


def render_list(items, ordered=False, start=1):
    """列表 -> HTML（两级嵌套；AIGC 卡渲染为 <span class="aigc">；
    任务项渲染为 class task / task-done，符号由主题 ::before 绘制）"""
    tag = "ol" if ordered else "ul"
    attrs = f' start="{start}"' if ordered and start != 1 else ""
    out = [f"<{tag}{attrs}>"]
    open_nested = False
    for it in items:
        if it["depth"] == 0:
            if open_nested:                 # 顶层项打断了嵌套层
                out.append(f"</{tag}></li>")
                open_nested = False
            frag = " fragment" if it["frag"] else ""
            extra = _task_cls(it)
            cls = (frag.strip() + (" " + extra if extra else "")).strip()
            attr = f' class="{cls}"' if cls else ""
            if it["callout"]:
                out.append(
                    f'<li class="callout-item{frag}">'
                    f'<span class="aigc">{it["text"]}</span>'
                )
            else:
                out.append(f"<li{attr}>{it['text']}")
        else:
            if not open_nested:
                out.append(f"<{tag}>")
                open_nested = True
            if it["callout"]:
                out.append(
                    f'<li class="callout-item"><span class="aigc">{it["text"]}</span></li>'
                )
            else:
                extra = _task_cls(it)
                attr = f' class="{extra}"' if extra else ""
                out.append(f"<li{attr}>{it['text']}</li>")
    if open_nested:
        out.append(f"</{tag}></li>")
    out.append(f"</{tag}>")
    return "".join(out)


def _task_cls(it):
    """任务项 -> class 片段：False=未完成 [ ]，True=已完成 [x]"""
    t = it.get("task")
    if t is False:
        return "task"
    if t is True:
        return "task task-done"
    return ""


def render_table(b):
    """表格 -> HTML（对齐 class 由主题控制；单元格走行内语法）"""
    def acl(i):
        a = b.aligns[i] if i < len(b.aligns) else "l"
        return "col-c" if a == "c" else "col-r" if a == "r" else ""

    out = ['<table class="tbl"><thead><tr>']
    for i, c in enumerate(b.header):
        out.append(f'<th class="{acl(i)}">{parse_inline(c)}</th>')
    out.append("</tr></thead><tbody>")
    for row in b.rows:
        out.append("<tr>")
        for i, c in enumerate(row):
            out.append(f'<td class="{acl(i)}">{parse_inline(c)}</td>')
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def render_content(slide, sec_no=0):
    # data-sec：页码供主题用 content: attr(data-sec) 生成 § 节号；
    # 对不使用它的主题（v1/v2）零视觉影响，向后兼容。
    title_html = parse_inline(slide.title) if slide.title else "&nbsp;"
    parts = [f'<header class="slide-header"><h2 data-sec="{sec_no}">{title_html}</h2></header>']
    body = []
    for b in slide.blocks:
        if b.kind == "h2":
            body.append(f'<h2 class="sec">{b.text}</h2>')
        elif b.kind == "h3":
            body.append(f"<h3>{b.text}</h3>")
        elif b.kind == "p":
            body.append(f"<p>{b.text}</p>")
        elif b.kind == "imgph":
            body.append(
                f'<div class="imgph"><span class="ph-ico"></span>'
                f"<span>{b.text}</span></div>"
            )
        elif b.kind == "mathd":
            body.append(f'<div class="math-display">{b.text}</div>')
        elif b.kind == "quote":
            # 引用块（容器语义）：大引号 + 左竖线由主题 .quote 样式绘制；
            # 内部的 aigc span 已在解析时透传，水印语义不受容器影响。
            body.append(f'<blockquote class="quote">{b.text}</blockquote>')
        elif b.kind == "ul":
            body.append(render_list(b.items))
        elif b.kind == "ol":
            body.append(render_list(b.items, ordered=True, start=b.start))
        elif b.kind == "table":
            body.append(render_table(b))
        elif b.kind == "code":
            lang = f' data-lang="{b.lang}"' if b.lang else ""
            body.append(f'<pre class="codeblock"{lang}><code>{b.text}</code></pre>')
        elif b.kind == "img":
            body.append(
                f'<figure class="figure"><img src="{b.src}" alt="{b.alt}"></figure>')
    parts.append('<div class="slide-body">' + "".join(body) + "</div>")
    return "".join(parts)


def render(slides, theme_css, runtime_js):
    n = len(slides)
    sections = []
    for i, s in enumerate(slides, 1):
        cls = "cover" if s.level == 1 else "content"
        inner = render_cover(s) if s.level == 1 else render_content(s, i)
        sections.append(
            f'  <section class="slide {cls}" data-i="{i}">\n'
            f"    {inner}\n"
            f'    <div class="pageno">{i}/{n}</div>\n'
            f"  </section>"
        )
    first_title = slides[0].title.strip() if slides and slides[0].title.strip() else "slides"
    title = first_title + " · mdshow"
    html = TEMPLATE
    html = html.replace("__TITLE__", title)
    html = html.replace("__THEME__", theme_css)
    html = html.replace("__RUNTIME__", runtime_js)
    html = html.replace("__SLIDES__", "\n".join(sections))
    return html
