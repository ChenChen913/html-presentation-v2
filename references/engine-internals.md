# 引擎机制、验证清单与已知陷阱

> 排障、二次开发引擎、或构建交付前的系统验证时读本文。
> 引擎原则：零第三方依赖、纯 Python 标准库、产物为完全自包含的单文件 HTML。

## 一、构建管线

```
讲稿.md ──parser.py──> Slide/Block 模型 ──render.py──> HTML（内联主题 CSS + runtime.js）──> 单文件产物
              │                           │
              └─ placeholders 警告         └─ 封面页(level=1) / 内容页(level=2, data-i/data-sec)
```

- `buildall` 参数：`source` 必填；`-o` 输出路径；`--dry-run` 只解析；`--theme` 主题 CSS（默认 v2 紫檀）；`--runtime` 一般不动。
- render 给每个内容页注入 `data-i`（页序，0 起）与 `data-sec`（节号，供主题 `attr(data-sec)` 生成题号）。
- 主题与运行时以 `<style>`/`<script>` 内联——产物离线可用，不依赖任何 CDN。

## 二、运行时（runtime.js）行为

- 舞台固定 1280×720，JS 按窗口等比缩放（transform: scale），任何屏幕/投影不变形。
- 键位：`←/→` 翻页 · `空格` 分步下一步 · `O` 总览网格 · `F` 全屏 · 点击右半屏翻页。
- hash 路由：`#/N`（N 从 1 起），**改动 hash 后必须 reload 才会生效**——刷新定位到第 N 页。
- 分步（fragment）：`.frag` 元素逐个显形；`{nf}` 标记的列表项不参与分步。

## 三、打印 / 导出 PDF

- `@page { size: 1280px 720px }`；主题需带 `print-color-adjust: exact`（不然色块被浏览器省墨算法洗白）。
- 打印时隐藏翻页 UI、展开全部分步元素；每页一纸，导出 PDF 即讲义。

## 四、交付前验证清单（Playwright 实操）

> 方法论：hash 导航视为同文档跳转，**导航后 reload 并等待 300–800ms** 再断言/截图；
> 早段跑过 emulate_media 或 hash 的 page 会残留状态——**总览类截图用全新 page 隔离**。

按七类逐项过（每类一句要点 + 操作）：

1. **无溢出**：7 页逐页 `document.documentElement.scrollWidth/Height` 不超舞台；截图目检。
2. **字号达标**：`getComputedStyle` 实测 标题 40+/正文 ≥28/注释 ≥20。
3. **对比度**：运行时实测 color 与向上找的真实背景（BG_FINDER 模式），逐对 ≥4.5:1。
4. **避头尾**：`lineBreak === "strict"` 且 `wordBreak !== "break-all"`。
5. **reduced-motion**：`page.emulate_media(reduced_motion="reduce")` 前后动画态双断言。
6. **打印**：emulate media "print" 后 `@page` 尺寸与色彩保留。
7. **交互冒烟**：方向键翻页页码 +1、O 键总览网格齐全。

## 五、已知陷阱（每条都真实踩过，勿再踩）

### 5.1 inline-block 基线拖歪列表符（v1/v2 曾有，v3 起修复）
CSS 规定 inline-block 的基线 = 其内部**最后一个行盒**的基线。长 `.aigc` 卡（inline-block）内部
换行时，同行 `li::marker` 会被拉到第二行。修法：`.aigc { display: inline; box-decoration-break: clone; }`
——既保持逐行水印底色，又不扰动基线。给新主题写水印样式时**禁止 inline-block**。

### 5.2 CSS 计数器对 display:none 页失效
放映引擎把非当前页 display:none，`counter-increment` 只计可见页 → 每页题号都显示 § 1。
修法（引擎级）：render 注入 `data-sec`，主题用 `content: attr(data-sec) ". "`。
注意：Chromium 的 `getComputedStyle` 会**求值 attr()**（返回展开结果），但**不求值 counter()**——
写断言时对 attr 展开值断言即可。题号符号用「N.」或纯数字，不用 §（西文法律引用符号）。

### 5.3 hash 导航格式与 reload
格式是 `#/3` 不是 `#3`；运行时只在启动时读一次 hash。自动化测试里 `goto(url#/3)` 后
**必须 reload**，并等待 300–800ms（分步动画与缩放计算需要时间）。

### 5.4 Makefile recipe 必须真 TAB
recipe 行首是 8 个空格时 make 报 "missing separator"。生成 Makefile 后跑
`grep -nP '^\s{8}\S' Makefile` 或直接 `sed -i 's/^    /\t/'` 修正。

### 5.5 中文字体零加载原则
主题字体栈只用系统字体（如 `"Songti SC", "SimSun", "Noto Serif CJK", serif`），**禁止引 Webfont**——
离线放映是硬需求。截图验证环境若无该字体，DejaVu 系会 fallback，字形不同但布局不炸。

### 5.6 深色主题的对比度要在板底上测
粉笔黄对板墨绿是 7.9:1，对白底只有 1.6:1——换深色主题时所有断言的底色都要跟随主题，
不能沿用浅色主题的断言底色。

### 5.7 图片占位符不是图片
`[[...]]` 只渲染占位卡；真实图片应替换为 Markdown 图片语法或 base64 内联（jyy 的 make-slides
约定：栅格图 embed base64 webp、downscale 到 720p；信息图优先用代码画——中文字符、白底、最强模型）。

## 六、二次开发指引

- **改视觉**：只动主题 CSS 的 `:root` 与组件区；不动 parser/render。
- **加块级语法**：parser.py 的行解析循环里加分支 + Block kind + render 的 `render_content` 分支；
  记得同步 `count_fragments`（若是分步元素）。
- **加主题**：复制 v3 或 v5 作骨架（两者分别代表"衬线暖底"与"无衬线冷底"两个极性），
  9 个分野维度至少改 6 个才算新主题（底色/字体/主色/骨架/水印/页码/列表符/着重号/行高）。
- 每次改动跑文末验证清单；改引擎必须对五套主题全部回归（引擎是共享层）。
