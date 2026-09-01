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


def render_ul(items):
    """列表 -> HTML（两级嵌套；AIGC 卡渲染为 <span class="aigc">）"""
    out = ["<ul>"]
    open_nested = False
    for it in items:
        if it["depth"] == 0:
            if open_nested:                 # 顶层项打断了嵌套层
                out.append("</ul></li>")
                open_nested = False
            frag = " fragment" if it["frag"] else ""
            if it["callout"]:
                out.append(
                    f'<li class="callout-item{frag}">'
                    f'<span class="aigc">{it["text"]}</span>'
                )
            else:
                cls = f' class="{frag.strip()}"' if frag else ""
                out.append(f"<li{cls}>{it['text']}")
        else:
            if not open_nested:
                out.append("<ul>")
                open_nested = True
            if it["callout"]:
                out.append(
                    f'<li class="callout-item"><span class="aigc">{it["text"]}</span></li>'
                )
            else:
                out.append(f"<li>{it['text']}</li>")
    if open_nested:
        out.append("</ul></li>")
    out.append("</ul>")
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
            body.append(
                f'<p class="callout fragment"><span class="aigc">{b.text}</span></p>'
            )
        elif b.kind == "ul":
            body.append(render_ul(b.items))
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
