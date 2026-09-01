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
8. **数学块不裸奔**：所有 `$$...$$` 页目检 `.math-display` 元素——内部文本不含
   `\`、`_{`、`^{`、`\frac` 等裸 LaTeX；浏览器 `getComputedStyle(.math-display).textContent`
   可脚本校验（diff 源稿：剥掉 `\\mid`、`\\prod` 等已知映射后还出现 `\` 即裸奔）。

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

### 5.8 展示数学块 `$$...$$` 不可借道 parse_inline（2026-09 dialect-test 翻车）
`mathd` 块的内部文本已剥掉 `$$` 定界符，再丢给 `parse_inline` 会让
`MATH_DISP_RE` / `MATH_INLINE_RE` 同时失配，**整行 LaTeX 原样转义输出**——
比"公式不渲染"更糟，因为它**不报错**。

修法是显式分流：parser 里 `mathd` 分支必须直接 `b.text = render_math(esc(m.group(1).strip()))`，
跳过 parse_inline 的全部规则链。规则："块级触发后还想偷懒复用行内函数"几乎必踩——
行内函数的正则匹配的是**含定界符的源码**，剥了定界符就是另一个东西了。

对每加一个块级语法分支都要问：内部文本还会带原定界符吗？若不会，渲染路径
必须独立，不能借道行内解析器。

## 六、二次开发指引

- **改视觉**：只动主题 CSS 的 `:root` 与组件区；不动 parser/render。
- **加块级语法**：parser.py 的行解析循环里加分支 + Block kind + render 的 `render_content` 分支；
  记得同步 `count_fragments`（若是分步元素）。
- **加主题**：复制 v3 或 v5 作骨架（两者分别代表"衬线暖底"与"无衬线冷底"两个极性），
  9 个分野维度至少改 6 个才算新主题（底色/字体/主色/骨架/水印/页码/列表符/着重号/行高）。
- 每次改动跑文末验证清单；改引擎必须对五套主题全部回归（引擎是共享层）。


## 附：jyy《生成式软件工程》开场白复刻实战（2026-09）

以 24 页原版截图为源做 1:1 内容复刻（v2 紫檀主题），验证并反哺了引擎：

- **原版同款陷阱**：长 aigc 卡跨行时列表符漂移到第二行（原版 tu07/tu10/tu13 可见）——
  即本文件第一章的 inline-block 基线问题；复刻稿用「追加覆盖」把 `.aigc` 改
  `display:inline + box-decoration-break:clone` 修复，原主题文件零改动。
- **原版翻车案例**：tu13 出现未渲染的 LaTeX 源码裸露（`$P(x_{1:n}\mid c)=...`）——
  引擎因此新增数学命令映射 + `_{}`/`^{}` 渲染（见 dialect-syntax.md 数学轻量渲染）；
  首版渲染采用容器整体斜体，实测观感刻意（用户反馈"只是英文字母加粗"），
  二次修订为词性分明排版：单字母变量 `<var>` 斜体、函数名/数字正体、
  `\mid` 改普通竖线 + 薄空格气口（详见 lessons-learned.md A1–A4）。
- **密度教训**：原版单页最多 7 个列表项 + 段落 + 长引用，720px 画布放不下。
  处置顺序：先在规范区间内收紧行高/间距（行高 1.5 下限、列表 gap 8px、
  安全边距 4%），仍超限再拆页（共拆 3 页：tu12、tu13、tu22 各拆为两页）。
  拆页标注「（续）」并在小节层级切分，内容一字未删。

## 六、第三轮修订：标准 Markdown 补全（2026-09）

全格式测试稿（examples/dialect-test/）暴露的缺口一次补齐，parser/render 各动一层：

- **新增块级五件套**：表格（lookahead 分隔行触发 + in_table 状态收集，单元格在渲染层
  走 parse_inline）、有序列表（`OL_ITEM_RE`，start 取首项号，遇非列表行才断开）、
  围栏代码块（状态机最优先，内容原样转义冻结）、任务列表（`- [ ]/[x]` → li.task）、
  真实图片（整行 → figure 居中图版，行内 → img.inline-img）。
- **方言预扫修正**：独立 `---` 判定跳过围栏代码块内的行，代码示例里写 --- 不再误翻方言 B。
- **行内顺序修正**（标准 Markdown 化）：行内代码最先暂存（内容冻结，`**x**` 可原样展示）
  → 行内图片 → 链接（图片必须排在链接前，否则感叹号被吃）→ 粗斜体 → 粗体 → 着重 →
  删除 → 数学 → 占位符 → 还原代码。
- **测试防线**：scripts/test_dialect_full.py 35 项引擎级断言 +
  scripts/verify_dialect.py 25 项 Playwright 断言（含逐页溢出、表格对齐、
  marker 颜色、::before 任务符号、图片加载与限高）；五主题全部补齐新元素样式
  （v2 完整版，v1/v3/v4/v5 基础款；v4/v5 线条式列表需显式关闭 ol li::before）。
## 附二：展示数学管线断接修复（2026-09 第四轮 · 用户报障驱动）

- **故障**：`examples/dialect-test/` 第 8 页行内公式渲染正常，独立一行的
  `$$P(x_{1:n} \mid c)=\prod_{i=1}^{n}...$$` 却整行裸奔源码——同页两种命运。
- **根因**：parse() 的 mathd 分支误用 parse_inline：`$$` 定界符在 fullmatch 时
  已被剥掉，而 parse_inline 内的数学规则（MATH_DISP_RE/MATH_INLINE_RE）按 `$`
  定界匹配，对新内容永远不命中 → 文本仅 esc 未渲染，原样进入
  `<div class="math-display">`。
- **修复**：`b.text = render_math(esc(m.group(1)))`——展示块语义即纯数学，
  直接走数学管线，不再借道通用行内解析。
- **为何三轮验证没抓到**：mathd 相关断言只查"节点存在"（mathd 块数、
  .math-display 是否出现），从未断言输出内容质量；测试稿里有 `$$...$$` 语法，
  引擎级测试（test_dialect_full.py）却没有对应条目——**语法写了 ≠ 测了**。
- **防线补齐**：test_dialect_full.py 新增 8b 组（mathd 块生成 / 内容含
  `<var>/<sub>/∏` / 无裸 `\mid _{ \prod` / 行中 `$$...$$` 走 math-d 路径回归），
  全格式引擎断言 35 → 39 项。
- **同页排障指纹**：一种样式好、一种坏 = 两条渲染管线不等价，先比对两条管线
  对同一内容的处理路径，再逐级打印中间产物。
