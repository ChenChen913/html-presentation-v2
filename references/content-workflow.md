# 内容生成工作流（源自 jyy make-slides 的完整转写）

> 本文档完整收录蒋炎岩（jyy）老师 `make-slides` 技能的**内容生成层**规则——
> 即"如何从讲义 + 片段产出幻灯片源稿"的工作流。mdshow-slides 引擎吃它的产物（方言 B），
> 两者是上下游关系。规则以中文转写，语义忠实于原版截图（tu03–tu06）。

## 一、输入与目标

- 输入两件套：**讲义全文**（路径）+ **一个片段（snippet，通常是讲义的一部分）**。
- 目标：为**且仅为给定片段**生成幻灯片源稿——不是全文。只产出 Markdown 片段，
  **不要标题页/结尾页**（cover/ending pages 不许有）。
- 先通读讲义全文（内容仅作背景 FYI），生成只围绕 snippet。

## 二、snippet 是逻辑线（最重要的一条）

- snippet 是**讲者的逻辑线**：Agent 可以延展、可以补充有价值的内容、可以给评论，
  但**不允许反驳、不允许越过 snippet 的观点**（Never reference later contents passing this
  snippet's point——不许引用跳过本片段之后才出现的内容）。
- 聚焦 snippet 本身。延展是"延展"，不是"替代"。

## 三、三路扇出（fan out three subagents）

对每一页，并行展开三个子任务（各给足上下文）：

1. **历史回顾**：这个主题的历史脉络、教训、事故、弯路。
2. **事实检索**：人类历史中的事实与相关工作——**不只是计算机科学**；
   优先采信公认的、高影响的结果。
3. **第一性原理**：从第一性原理重新推导一遍。

三路结果回收后定稿：**不写琐碎的总结与推导**（"这个我知道、上课会讲"的东西不进片）；
保持简洁、有思想、有洞见；**只收敛到真正有用的增量**（only converge to really useful add-ups）。

## 四、AIGC 扩写约定

- `[[...]]` 包住的部分 = **请求 AIGC 扩写**，必须展开。
  （注：mdshow 引擎把 `[[...]]` 渲染为图片占位卡；若按本工作流用作扩写请求，
  扩写后请**移除** `[[...]]` 记号再交付，两种用法不要叠加在同一处。）
- Agent 自己新增的文字：包 `<span class="aigc">`；**轻微改写的文字不要包**，
  避免大量 aigc 污染片（dilute the signal）。
- `#`/`h1`/`h2` 标题里**不用 aigc**，即使是 AI 生成的标题；不用 metadata。

## 五、版面 Style（原文规则的中文转写）

- 列表内容常常有嵌套：优先嵌套列表，嵌套层级按内容需要 ≥ 2 层。
- 每页一个 `h1`（Title Case）；每页 1–2 个 `h2`（主要点）；每页 bullets **总数 ≤ 8**。
- 有图的页：图可以大，**其他内容保持极简**；一页最多 1 张图。
- 页与页用 `---` 分隔。
- 数学：行内 `$...$`、展示式 `$$...$$`；**逐条检查数学语法正确**。

## 六、图与图的生成

- **不生成图，除非被要求**（No generated diagrams unless instructed）。
- 需要栅格图时：embed base64 webp，downscale 到 720p。
- 在 subagent 里生成图片时：**优先信息图（diagram with information）**、
  图内文字用中文字符、白底、用最强的模型。

## 七、Headless 产物约定

- 技能以 headless 方式运行：把产物写到 `/tmp/slides.md` 后**立即退出，无输出**。
- mdshow 侧的收编方式：`make accept`（把 /tmp/slides.md 收进仓库并构建预览；
  引擎自动按方言 B 解析——`---` 分页）。

## 八、与 mdshow-slides 的衔接

```
讲义全文 + snippet ──(本文档一~六章的工作流)──> /tmp/slides.md（方言 B）
                                                    │
mdshow 引擎 buildall ──theme + palette──> 单文件 HTML 放映稿
```

- 产物格式校验：方言 B 语法表 → `dialect-syntax.md` 第二章。
- 产物版面红线（对比度/字号/避头尾）：→ `design-system.md`。
- 构建与验证：→ `SKILL.md` 快速上手 + `engine-internals.md` 第四章。
