# 示例 · 《生成式软件工程》开场白（27 页实战稿）

用「紫檀 v2」模板 1:1 复刻 jyy 老师《生成式软件工程》课程开场白课件
（24 张原版截图 → 按每页 ≤8 要点规范拆为 27 页，内容零删减）。

这是本引擎在**真实高密度课程课件**上的完整实战验证稿。

## 文件

| 文件 | 说明 |
|---|---|
| `nanda-gense.md` | 讲稿源稿（方言 A，## 分页） |
| `nanda-gense.html` | 构建产物：27 页 / 125 分步元素，单文件双击放映 |
| `theme-v2-nanda.css` | 合成主题 = 紫檀 v2 本体 + 高密度 override（已内联进 HTML） |
| `theme-nanda-override.css` | 追加覆盖片段（引用块样式 / 高密度档参数） |
| `preview/` | 关键页截图（封面 / 数学页 ×2） |

## 涉及的语法能力

引用块（含内嵌 AIGC 水印）、行内/展示数学（词性分明排版 + 断行策略）、
删除线、上下标、着重号、图片占位卡、高密度排版参数。

## 重建

```bash
python3 assets/engine/buildall examples/nanda-gense/nanda-gense.md \
  -o examples/nanda-gense/nanda-gense.html \
  --theme examples/nanda-gense/theme-v2-nanda.css
```

> 源稿中 `[[...]]` 图片占位符为刻意保留（对应原版课件截图位置），
> 构建时的警告属预期行为。
