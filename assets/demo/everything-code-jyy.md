# A Bold Experiment

## 这学期的实验

- 这门课的所有课件，都由讲义 + Agent 实时扩写生成
- <span class="aigc">讲义是我的逻辑线：Agent 只做延展，不许反驳、不许越过我的观点</span>
- <span class="aigc">你看到的每一页都是构建产物：可以重新生成、可以 diff、可以回滚</span>

---

# Text Is The Source Of Truth

## 文本是唯一事实源

- 文本是 source of truth：文字讲义是唯一手工维护的东西
- <span class="aigc">图片、网页、视频切片等其他模态，全部视为 AIGC 产物</span>
- <span class="aigc">改文字就是改源码：重新构建，所有模态随之更新</span>

## 为什么坚持文本

- <span class="aigc">像素无法 diff，录像无法 merge，二进制无法审阅</span>
- 文本可审阅：每一页都读得懂、改得动、管得住版本

---

# Everything is code

## 这套 slides 如何工作?

- 文本是 source of truth：你看到的其他模态都是 AIGC
- <span class="aigc">完整讲义提供上下文 → 选中的 snippet 划定边界 → Agent 扩写 → Markdown slides → 浏览器渲染</span>
- <span class="aigc">生成内容统一标记为 aigc：逻辑改变时修改源码，图片、网页和视频切片都可以重新生成</span>

## 要“永生”的不是一份录像

- <span class="aigc">保存可编辑、可 diff、可复现的源代码与构建过程，而不只是最终像素</span>
- 如果成功，就“永生”我的操作系统课

---

# The Make-Slides Skill

## 一个技能，两个输入

- 讲义文件：完整读取，仅作上下文（FYI）
- snippet：我选中的一段逻辑线，**唯一**的成稿范围
- <span class="aigc">产物只有 markdown 片段：不生成封面，不生成致谢页</span>

## 三个专家子代理，逐页扇出

- <span class="aigc">历史钩沉：这门技术来路上的经验、教训与事故</span>
- <span class="aigc">人文事实：在人类历史（而非仅在计算机科学）中寻找公认、高影响的关联工作</span>
  - <span class="aigc">例如：从古登堡印刷术到晶体管，而不只是从 ENIAC 到 GPU</span>
- <span class="aigc">第一性原理：从本源重新推一遍，检验逻辑是否成立</span>
- <span class="aigc">三路结果收敛成稿：禁止 trivial 总结——那些我课上会讲</span>

---

# Aigc, Clearly Marked

## 水印规范

- <span class="aigc">Agent 新增的一切文本必须包进 span.aigc：观众有权知道每句话是谁写的</span>
- 小幅改写不打标：避免满屏 aigc，稀释水印的信息量
- <span class="aigc">标题永不打标：h1/h2 即使由 AI 生成，也保持素面</span>

## 硬性排版约束

- 每页一个 h1 标题（Title Case），1-2 个 h2 小节
- 每页 bullets 总数 ≤ 8；最多 1 张图，图大字少
- <span class="aigc">数学一律 $inline$ 与 $$display$$，落盘前逐条检查语法</span>

---

# Immortality, Via Code

## 永生的三个条件

- <span class="aigc">可编辑：换一种讲法，改几行文本重新构建即可</span>
- <span class="aigc">可 diff：两个学年的课件差异，就是一次 git diff</span>
- <span class="aigc">可复现：源码与构建脚本还在，slides.html 随时重来</span>

## 这套课件的自我描述

- 你正在看的这 6 页，本身就是 make-slides 方言的示范稿
- 如果成功，就“永生”我的操作系统课
