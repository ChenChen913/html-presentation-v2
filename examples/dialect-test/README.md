# 示例 · Markdown 全格式测试稿（活语法表）

一份讲稿测尽引擎支持的全部格式：既是**回归测试稿**，也是**活的语法参考**。
每页演示一类语法，可直接放映查看真实渲染效果。

## 文件

| 文件 | 说明 |
|---|---|
| `dialect-test.md` | 测试稿源稿（方言 A，13 页） |
| `dialect-test.html` | 构建产物（紫檀 v2 主题，单文件放映） |
| `assets/sample-figure.png` | 本地相对路径图片（测 `![alt](src)` 真实图片） |
| `preview/` | 关键页截图 |

## 覆盖清单

**块级**：封面 / `##` 分页 / `###` 小节 / 无序+嵌套列表 / `{nf}` 关闭分步 /
有序列表（`start` 起始号）/ 表格（四档对齐 + 单元格行内语法）/ 围栏代码块
（语言徽标）/ 任务列表（☐/☑）/ 引用块（内嵌 AIGC 水印）/ 真实图片 /
`[[...]]` 占位卡 / 展示数学 `$$...$$`

**行内**：粗体 / 着重号 / 删除线 / 粗斜体 / 行内代码（内容冻结不解析）/
超链接 / 行内数学（词性分明 + 竖线气口）/ 行内图片 / 行内占位标记

**边界（演示页内说明）**：`---` 会翻转方言 B、不支持脚注/定义列表/多行单元格。

## 重建

```bash
python3 assets/engine/buildall examples/dialect-test/dialect-test.md \
  -o examples/dialect-test/dialect-test.html \
  --theme references/themes/theme-v2-zitan.css
```

> 注意：`assets/sample-figure.png` 为本地相对路径，HTML 与 assets 目录
> 需保持相对位置；外链图片 URL 亦可，但离线放映时不可达。
