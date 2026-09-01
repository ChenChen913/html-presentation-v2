---
name: mdshow-slides
description: 用 Markdown 生成单文件 HTML 学术演示文稿（幻灯片/slides/放映稿/PPT 替代品）——零依赖纯 Python 构建引擎 + 五套风格主题 + 五大高校色系（南京大学紫/武汉大学绿/北京大学红/浙江大学蓝/墨板黑）。只要用户提到"做 slides / 幻灯片 / 演示文稿 / 把讲稿或 Markdown 变成 PPT / 课程讲义放映 / 学术风演示 / 按某大学配色做 PPT"，或内容中出现 AIGC 标记、[[图片占位符]]、make-slides 风格的讲稿片段，就应该使用本 skill——即使用户没有明确说"HTML"。
---

# mdshow-slides · 讲稿即代码

> 背景故事与完整致谢 → 仓库主页 [README.md](README.md)。

## 核心理念（为什么是这样）

- **文本是 source of truth**：你看到的每一页 HTML 都是 Markdown 讲稿的构建产物，可 diff、可回滚、可重新生成。
- **AIGC 如实标记**：凡是 AI 扩写的内容，源稿中必须包在 `<span class="aigc">…</span>` 里，主题会渲染出可辨识的水印底色——这是对听众的诚实，也是这套工作流的灵魂，不许省略。
- **单文件交付**：构建产物是一个 HTML（引擎 + 主题 + 讲稿内容全部内联），双击即可放映，无网络、无依赖。

## 快速上手（三条命令）

```bash
# 1. 把 assets/engine/ 拷到工作区（或直接用 skill 内路径）
cp -r <skill>/assets/engine ./engine

# 2. 写讲稿（语法见下节速查，完整表见 references/dialect-syntax.md）
#    引用现成模板：assets/demo/everything-code-jyy.md

# 3. 构建（--theme 换主题，默认 v2 紫檀）
python3 engine/buildall 讲稿.md -o slides.html --theme <skill>/references/themes/theme-v3-paper-journal.css
```

产物直接双击打开放映。键位：`←/→` 翻页 · `空格` 下一步（分步动画）· `O` 总览 · `F` 全屏 · 点击右半屏翻页。打印/导出 PDF：浏览器打印，页面尺寸已按 1280×720 预置。

## 双方言语法速查（完整表 → references/dialect-syntax.md）

引擎自动识别两种方言，无需配置：

| | 方言 A「人类讲稿」 | 方言 B「make-slides 产物」 |
|---|---|---|
| 分页 | `## 标题`（二级标题即新页） | `---` 水平线分页 |
| 封面 | 文档第一个 `# 一级标题` | 第一页即封面 |
| 渐进显示 | 列表项 = 分步元素 | 同左（`*`/`-` 逐项出现） |

行内语法：`**粗体**`、`*着重*`（主题渲染为着重号，不用伪斜体）、`` `行内码` ``、`[链接](url)`、
`<span class="aigc">AI 扩写内容</span>`（AIGC 水印）、`[[图片说明]]`（渲染为虚线占位卡，提醒补图）。

## 五主题 × 五色系（决策树）

**第一步：选主题骨架**（完整风格档案 → references/design-system.md 第二章）

| 主题 | 文件（references/themes/） | 风格 | 默认色系 | 适合 |
|---|---|---|---|---|
| v1 紫罗兰讲台 | `theme-v1-nju-replica.css` | jyy 原版 1:1 复刻 | 紫 | 忠实复刻南大课堂感 |
| v2 紫檀 | `theme-v2-zitan.css` | 现代规范版、紫渐变色块 | 紫 | 通用学术汇报（默认推荐） |
| v3 纸墨学刊 | `theme-v3-paper-journal.css` | 衬线宋体、暖纸底、学刊双细线 | 红 | 人文/论文陈述、纸质学术感 |
| v4 墨板讲堂 | `theme-v4-chalkboard.css` | 黑板粉笔、楷体 | 绿黑 | 大班授课、课堂讲授 |
| v5 瑞士图则 | `theme-v5-swiss-blueprint.css` | 白底墨字、克莱因蓝、直角细线 | 蓝 | 工程/设计向、国际主义排版 |

**第二步：按大学换色系**（官方色值与完整 token → references/university-palettes.md；
可直接引入的变量覆盖片段 → assets/palettes/palette-{purple|green|red|blue|black}.css）

| 色系 | 代表大学（官方标准色） | 片段文件 |
|---|---|---|
| 紫 | 南京大学 · 南大紫（C50 M100 Y0 K40）；清华大学 · 紫白 | `palette-purple.css` |
| 绿 | 武汉大学 · 珞珈绿（#115740）；中山大学 · 标准绿（C100 M0 Y100 K60） | `palette-green.css` |
| 红 | 北京大学 · 北大红（#94070A）；中国人民大学 · 人大红 | `palette-red.css` |
| 蓝 | 浙江大学 · 求是蓝（≈#003F88）；武汉大学 · 珞珈蓝（#002554） | `palette-blue.css` |
| 黑 | 墨色系（无彩色学术风，任何学校通用；黑板/水墨意象） | `palette-black.css` |

用法（追加覆盖法，已验证）：打开片段文件，把与所用主题对应的 `:root` 块**追加到主题 CSS 文件末尾**，
另存为新主题（如 `theme-v3-pku-red.css`）后照常构建——CSS 同名变量后者生效，原主题保持可回滚。
v1 是忠实复刻主题，不建议换色；v2–v5 均为全变量化设计，换色零风险。

## 写稿规则（速查，溯源与理由 → references/design-system.md）

> 若你的任务是**生成讲稿内容**（而不只是把现成 Markdown 转成放映稿），
> 先读 `references/content-workflow.md`——jyy make-slides 的内容层工作流：snippet 逻辑线、
> 三路扇出、AIGC 约定、版面 Style、headless 产物约定。

- 每页 ≤ 8 个要点（总数），嵌套列表 ≥ 2 层时改用小节（`###`）；标题不用 AIGC 标记。
- AI 扩写必须 `<span class="aigc">` 包裹；轻微改写的文字不要包，避免水印泛滥。
- 一页最多 1 张图；`[[...]]` 占位符构建时会控制台告警，交付前应替换为真实图片。
- 中文排版红线：正文行高 1.7、`line-break: strict` 避头尾、字距只加标题、纯黑 `#000` 禁止（用带色相深墨）。
- 标题编号用「N.」或纯数字即可；**不要用 § 符号**（西文法律引用符号，中文标号不适用，2026-09 与用户确认移除）。

## 构建与验证（陷阱手册 → references/engine-internals.md）

- 构建是纯 Python 标准库，零第三方依赖；`--dry-run` 只解析检查不写文件。
- 交付前建议用 Playwright（或手动）过一遍：7 类检查 = 无溢出 / 字号达标 / 对比度 ≥ 4.5:1 / 避头尾 / reduced-motion / 打印样式 / 交互冒烟。逐项操作细节见 engine-internals.md 第四章。
- 已知陷阱速记：inline-block 基线会拖歪列表符（`.aigc` 用 `display:inline`）、CSS 计数器对隐藏页失效（节号由引擎注入 `data-sec`）、hash 导航格式是 `#/3` 且需 reload。

## 文件地图（按需读取，勿一次全读）

```
mdshow-slides/
├── SKILL.md                        ← 你在这里（主流程）
├── README.md / README_EN.md        # 项目主页（中/英，特性总览与致谢）
├── LICENSE                         # MIT
├── references/
│   ├── dialect-syntax.md           # 双方言语法全表（写稿前速览一次）
│   ├── content-workflow.md         # 内容生成工作流（jyy make-slides 转写：三路扇出/snippet 逻辑线）
│   ├── design-system.md            # 设计规范 + 五主题风格档案（选主题/写样式时读）
│   ├── university-palettes.md      # 五色系 × 大学官方色值 × token 映射（换色时读）
│   ├── engine-internals.md         # 引擎机制、验证清单、已知陷阱（排障时读）
│   └── themes/                     # ★ 五套主题模板 CSS（构建 --theme 的取材处）
└── assets/
    ├── engine/                     # ★ 放映引擎（纯 Python + runtime.js，拷走即用）
    │   ├── buildall                #   构建入口
    │   └── slideshow/              #   parser / render / runtime.js
    ├── palettes/                   # ★ 五色系变量覆盖片段（紫/绿/红/蓝/黑）
    ├── demo/                       # 示例讲稿（everything-code-jyy.md，方言 B 全语法）
    └── showcase/                   # ★ 五主题成品预览（HTML + 截图，选型时目测参考）
```
