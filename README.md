<div align="center">

[**简体中文**](README.md) · [English](README_EN.md)

# 🎓 mdshow-slides · 讲稿即代码

**用 Markdown 写讲稿，一条命令构建单文件 HTML 学术演示文稿**

讲稿是唯一事实源（source of truth），幻灯片只是构建产物 —— 可 diff、可回滚、可重新生成。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/Dependencies-zero-brightgreen)](README.md#-特性)
[![Output](https://img.shields.io/badge/产物-单文件%20HTML-orange)](README.md#-快速开始)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/ChenChen913/html-presentation-v2/pulls)

[![紫 · 南京大学](https://img.shields.io/badge/%E7%B4%AB%20%C2%B7%20%E5%8D%97%E4%BA%AC%E5%A4%A7%E5%AD%A6-%234D0099-4D0099)](README.md#-五大高校色系)
[![绿 · 武汉大学](https://img.shields.io/badge/%E7%BB%BF%20%C2%B7%20%E6%AD%A6%E6%B1%89%E5%A4%A7%E5%AD%A6-%23115740-115740)](README.md#-五大高校色系)
[![红 · 北京大学](https://img.shields.io/badge/%E7%BA%A2%20%C2%B7%20%E5%8C%97%E4%BA%AC%E5%A4%A7%E5%AD%A6-%2394070A-94070A)](README.md#-五大高校色系)
[![蓝 · 浙江大学](https://img.shields.io/badge/%E8%93%9D%20%C2%B7%20%E6%B5%99%E6%B1%9F%E5%A4%A7%E5%AD%A6-%23003F88-003F88)](README.md#-五大高校色系)
[![黑 · 墨色系](https://img.shields.io/badge/%E9%BB%91%20%C2%B7%20%E5%A2%A8%E8%89%B2%E7%B3%BB-%232B2735-2B2735)](README.md#-五大高校色系)

[![Stars](https://img.shields.io/github/stars/ChenChen913/html-presentation-v2?style=social)](https://github.com/ChenChen913/html-presentation-v2/stargazers)
[![Issues](https://img.shields.io/github/issues/ChenChen913/html-presentation-v2)](https://github.com/ChenChen913/html-presentation-v2/issues)

</div>

---

## 💡 这是什么

**mdshow-slides** 是一套"讲稿即代码"的幻灯片工作流：你只负责写 Markdown 讲稿，构建引擎把它编译成一个 **单文件 HTML**——引擎、主题、内容全部内联，双击即可放映，无网络、无依赖、无外部字体。构建器是纯 Python 标准库实现（约 700 行），任何装了 Python 3.8+ 的机器都能直接跑。

它同时也是一个 **AI Agent Skill**：仓库本身就是标准的三层技能结构（`SKILL.md` 主流程 + `references/` 深度文档 + `assets/` 可执行资产），克隆后放进 `.agents/skills/` 目录，你的编码智能体就能按照规程替你造稿、构建、验收。

- 🎨 **五套主题**：从 1:1 复刻的南大课堂，到学刊衬线、黑板粉笔、瑞士国际主义排版
- 🏫 **五大高校色系**：紫（南京大学）/ 绿（武汉大学）/ 红（北京大学）/ 蓝（浙江大学）/ 黑（墨色系），官方色值逐一核实
- 🤥 **AIGC 如实标记**：AI 扩写的内容渲染出可辨识的水印底色——对听众诚实

## ✨ 特性

| 特性 | 说明 |
|---|---|
| 📝 讲稿即代码 | Markdown 是唯一事实源，幻灯片可重新生成；改样式不动内容，改内容不动样式 |
| 🔀 双方言自动识别 | 人类讲稿（`##` 分页）与 make-slides 产物（`---` 分页）混合写也能正确解析，零配置 |
| 📦 单文件交付 | 产物一个 HTML（15–27 KB），可进 Git、可邮件发送、可离线放映 |
| 🖱️ 完整放映交互 | `←/→` 翻页 · 空格分步 · `O` 总览网格 · `F` 全屏 · 点击/触屏滑动 · `#/n` 直达某页 |
| 🤥 AIGC 水印 | `<span class="aigc">` 包裹 AI 扩写内容，主题渲染 ✦ 水印底色，如实告知听众 |
| 🖨️ 打印即 PDF | `@page` 已按 1280×720 预置分页，浏览器打印对话框直接导出讲义 |
| 🖼️ 图片占位卡 | `[[图片说明]]` 渲染为虚线占位卡，构建时控制台告警提醒补图 |
| ♿ 排印合规 | 字号梯度、对比度 ≥ 4.5:1、避头尾、着重号代替伪斜体、`prefers-reduced-motion` 全部内建 |

## 🚀 快速开始

```bash
# 1. 拿到引擎（本仓库即技能目录，engine 在 assets/ 下）
git clone https://github.com/ChenChen913/html-presentation-v2.git
cd html-presentation-v2

# 2. 写一份讲稿（可以从示例改起）
cp assets/demo/lecture-demo.md my-lecture.md

# 3. 构建（--theme 换主题，默认 v2 紫檀）
python3 assets/engine/buildall my-lecture.md -o slides.html \
    --theme references/themes/theme-v3-paper-journal.css
```

构建完成，`slides.html` 双击即可放映。键位：`←/→` 翻页 · `空格` 下一步（分步动画）· `O` 总览 · `F` 全屏 · 点击右半屏翻页。导出 PDF：浏览器打印（页面尺寸已预置）。

> 想先看效果？直接打开 [`assets/showcase/`](assets/showcase/) 里五个构建好的成品 HTML 双击放映。

## 🎨 五套主题

同一篇讲稿在五套主题下的真实构建产物（点开大图见 [`assets/showcase/`](assets/showcase/)）：

<table>
  <tr>
    <td align="center"><img src="assets/showcase/preview/showcase-v1-nju-replica-p1.png" width="260" alt="v1 紫罗兰讲台"><br><sub><b>v1 紫罗兰讲台</b> · jyy 原版 1:1 复刻</sub></td>
    <td align="center"><img src="assets/showcase/preview/showcase-v2-zitan-p1.png" width="260" alt="v2 紫檀"><br><sub><b>v2 紫檀</b> · 现代规范版（默认推荐）</sub></td>
    <td align="center"><img src="assets/showcase/preview/showcase-v3-paper-journal-p1.png" width="260" alt="v3 纸墨学刊"><br><sub><b>v3 纸墨学刊</b> · 衬线宋体 · 学刊双细线</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/showcase/preview/showcase-v4-chalkboard-p1.png" width="260" alt="v4 墨板讲堂"><br><sub><b>v4 墨板讲堂</b> · 黑板粉笔 · 楷体板书</sub></td>
    <td align="center"><img src="assets/showcase/preview/showcase-v5-swiss-blueprint-p1.png" width="260" alt="v5 瑞士图则"><br><sub><b>v5 瑞士图则</b> · 白底墨字 · 克莱因蓝</sub></td>
    <td align="center"><sub><a href="assets/showcase/"><b>▶ 打开 showcase</b><br>五个成品 HTML<br>双击即可放映</a></sub></td>
  </tr>
</table>

| 主题 | 模板文件 | 风格 | 适合场景 |
|---|---|---|---|
| v1 紫罗兰讲台 | `theme-v1-nju-replica.css` | 南大课堂原版复刻 | 忠实复刻课堂感（不建议换色） |
| v2 紫檀 | `theme-v2-zitan.css` | 现代规范版、紫渐变色块 | 通用学术汇报（**默认推荐**） |
| v3 纸墨学刊 | `theme-v3-paper-journal.css` | 衬线宋体、暖纸底、学刊双细线 | 人文/论文陈述 |
| v4 墨板讲堂 | `theme-v4-chalkboard.css` | 黑板粉笔、楷体 | 大班授课 |
| v5 瑞士图则 | `theme-v5-swiss-blueprint.css` | 白底墨字、克莱因蓝、直角细线 | 工程/设计向 |

## 🏫 五大高校色系

主题骨架之外，每个主题都可一键换成对应高校的官方色系（变量覆盖片段在 [`assets/palettes/`](assets/palettes/)，官方色值来源见 [`references/university-palettes.md`](references/university-palettes.md)）：

| 色系 | 代表大学 | 官方标准色 | 覆盖片段 |
|---|---|---|---|
| 🟣 紫 | 南京大学 | 南大紫 C50 M100 Y0 K40（2010 版视觉形象规范） | `palette-purple.css` |
| 🟢 绿 | 武汉大学 | 珞珈绿 `#115740`（官网发布） | `palette-green.css` |
| 🔴 红 | 北京大学 | 北大红 `#94070A`（标识管理办公室） | `palette-red.css` |
| 🔵 蓝 | 浙江大学 | 求是蓝 ≈`#003F88`（校方 VI） | `palette-blue.css` |
| ⚫ 黑 | 墨色系（通用） | 无彩色学术风，任何学校通用 | `palette-black.css` |

换色方法（追加覆盖法，已验证）：把片段文件中对应主题的 `:root` 块**追加到主题 CSS 末尾**，另存为新主题后照常构建——CSS 同名变量后者生效，原主题保持可回滚。v2–v5 均为全变量化设计，换色零风险。

## ✍️ 语法速查

引擎自动识别两种方言，无需配置：

| | 方言 A「人类讲稿」 | 方言 B「make-slides 产物」 |
|---|---|---|
| 分页 | `## 标题`（二级标题即新页） | `---` 水平线分页 |
| 封面 | 文档第一个 `# 一级标题` | 第一页即封面 |
| 渐进显示 | 列表项 = 分步元素 | 同左（逐项出现） |

行内语法：`**粗体**` · `*着重*`（渲染为着重号，不用伪斜体）· `` `行内码` `` · `[链接](url)` · `<span class="aigc">AI 扩写内容</span>`（AIGC 水印）· `[[图片说明]]`（虚线占位卡）

完整语法表 → [`references/dialect-syntax.md`](references/dialect-syntax.md)；写稿规范（每页 ≤8 要点、AIGC 使用边界等）→ [`SKILL.md`](SKILL.md) 与 [`references/content-workflow.md`](references/content-workflow.md)。

## 🤖 作为 AI Skill 使用

仓库本体即技能目录，结构符合 Agent Skill 三层规范（渐进式披露：主文件只放主流程，深度内容按需下放）：

```bash
mkdir -p .agents/skills
git clone https://github.com/ChenChen913/html-presentation-v2.git .agents/skills/mdshow-slides
```

之后对智能体说"**用 mdshow-slides 给这个讲稿做一个幻灯片**"即可。技能内部约定：

- `SKILL.md` —— 主流程：选主题、换色系、写稿规则、构建命令（约百行，刻意精简）
- `references/` —— 语法全表 / 内容生成工作流 / 设计系统 / 高校色值 / 引擎陷阱手册 / 五主题模板
- `assets/` —— 放映引擎 / 五色系片段 / 示例讲稿 / 五个成品 showcase

## 📁 目录结构

```
html-presentation-v2/
├── README.md                       # 本文件（中文，默认）
├── README_EN.md                    # English version
├── LICENSE                         # MIT
├── SKILL.md                        # ★ 技能主文件（主流程）
├── references/
│   ├── dialect-syntax.md           #   双方言语法全表
│   ├── content-workflow.md         #   内容生成工作流（snippet 逻辑线 / 三路扇出）
│   ├── design-system.md            #   设计规范 + 五主题风格档案
│   ├── university-palettes.md      #   五色系 × 大学官方色值
│   ├── engine-internals.md         #   引擎机制 / 验证清单 / 已知陷阱
│   └── themes/                     # ★ 五套主题模板 CSS
└── assets/
    ├── engine/                     # ★ 放映引擎（纯 Python + runtime.js）
    ├── palettes/                   # ★ 五色系变量覆盖片段
    ├── demo/                       #   示例讲稿
    └── showcase/                   # ★ 五主题成品预览（HTML + 截图）
```

## 🙏 致谢

本工作流受**南京大学蒋炎岩（jyy）老师**的课程幻灯片（操作系统 / 生成式软件工程）及其
`make-slides` 技能工作流启发：讲稿是唯一事实源（source of truth），幻灯片是构建产物；
AI 扩写的内容一律用 `.aigc` 水印如实标记。向 jyy 老师开源分享这一工作流致敬。

- jyy 主页：<https://jyy.website/>
- 本仓库中 v1 主题即对其课堂幻灯片风格的 1:1 复刻，仅作学习交流用途。

## 📄 开源许可

[MIT](LICENSE) © 2026 ChenChen913

主题中的高校配色参考各校公开的视觉形象规范，版权归原作者/学校所有，仅作学习交流用途。

<div align="center">

**如果这个项目对你有帮助，欢迎点一个 ⭐**

</div>
